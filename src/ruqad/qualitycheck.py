#!/usr/bin/env python3

# This file is a part of the RuQaD project.
#
# Copyright (C) 2024 IndiScale GmbH <www.indiscale.com>
# Copyright (C) 2024 Daniel Hornung <d.hornung@indiscale.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
"""

# TODO Use Gitlab Python module instead of curl. Or at least the requests module.

import argparse
import json
import os
import time
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Optional
from zipfile import ZipFile

import boto3
import toml


def read_config() -> dict:
    """Read config from ``./qualitycheck_config.toml``.

This config file must define the following:

- ``s3_endpoint``: S3 endpoint to connect to.
- ``s3_bucket``: Bucket in the S3 Service.

Returns
-------
out: dict
  The config.
    """
    config = toml.load("./qualitycheck_config.toml")
    assert "s3_endpoint" in config
    assert isinstance(config["s3_endpoint"], str)
    assert "s3_bucket" in config
    assert isinstance(config["s3_bucket"], str)

    return config


class QualityChecker:

    class CheckFailed(RuntimeError):
        def __init__(self, reason: dict):
            super().__init__()
            self.reason = reason

    def __init__(self):
        """The QualityChecker can do quality checks for content.
        """
        self._config = read_config()
        secret_vars = [
            "S3_ACCESS_KEY_ID",
            "S3_SECRET_ACCESS_KEY",
            "GITLAB_PIPELINE_TOKEN",
            "GITLAB_API_TOKEN",
        ]
        missing = False
        for varname in secret_vars:
            try:
                self._config[varname.lower()] = os.environ[varname]
            except KeyError:
                print(f"This environment variable is missing: {varname}")
                missing = True
        if missing:
            raise RuntimeError("Missing environment variables.")

        self._bucketname = self._config["s3_bucket"]
        session = boto3.Session(aws_access_key_id=self._config["s3_access_key_id"],
                                aws_secret_access_key=self._config["s3_secret_access_key"])
        self._s3_client = session.client("s3", endpoint_url=self._config["s3_endpoint"])

    def check(self, filename: str, target_dir: str = ".") -> bool:
        """Check for data quality.

Parameters
----------

filename : str
  The file to be checked.

target_dir : str, default="."
  Download to this directory.

Returns
-------
out : bool
  True if the checks passed, false otherwise.
        """
        # Prepare check
        self._upload(filename)

        # Actual check
        check_ok = True
        try:
            pipeline_id = self._trigger_check()
            job_id = self._wait_for_check(pipeline_id=pipeline_id)
            self._download_result(job_id=job_id, target_dir=target_dir)
        except self.CheckFailed as cfe:
            print(f"Check failed:\nStatus: {cfe.reason['status']}")
            breakpoint()

            check_ok = False

        # Cleanup
        self._cleanup()

        return check_ok

    def _cleanup(self):
        """Clean up the S3 bucket.

This deletes all the objects in the bucket.
        """
        objects = self._s3_client.list_objects_v2(Bucket=self._bucketname).get("Contents")
        if objects is None:
            # nothing to delete
            return
        for obj in objects:
            self._s3_client.delete_object(Bucket=self._bucketname, Key=obj["Key"])

    def _extract_content(self, filename: str, upload: bool = False):
        """Extract content from the archive.  May also upload to S3.

        Parameters
        ----------
        filename : str

        upload : bool, default=False
        """
        with TemporaryDirectory() as tmp:
            if not tmp.endswith(os.path.sep):
                tmp = tmp + os.path.sep
            zipf = ZipFile(filename)
            zipf.extractall(path=tmp)  # TODO Zip bomb detection and prevention.
            for name in zipf.namelist():
                if name.endswith(".json") or name.endswith(os.path.sep):
                    continue
                if upload:
                    self._upload(os.path.join(tmp, name), remove_prefix=tmp)

    def _upload(self, filename: str, remove_prefix: Optional[str] = None):
        """Upload the file to the S3 bucket.

Compressed files (with suffix .zip or .eln) will be extracted first.

Parameters
----------
filename : str
  The file to be checked.

remove_prefix : Optional[str]
  If given, remove this prefix from the filename when storing into the bucket.
        """
        # Check file type first.
        if Path(filename).suffix in [".eln", ".zip"]:
            self._extract_content(filename, upload=True)
            return

        target_filename = filename
        if remove_prefix:
            if not filename.startswith(remove_prefix):
                raise ValueError(f"{filename} was expected to start with {remove_prefix}")
            target_filename = filename[len(remove_prefix):]
        self._s3_client.upload_file(filename, self._bucketname,
                                    os.path.join("data", target_filename))

    def _trigger_check(self) -> str:
        """Trigger a new pipeline to start quality checks.

    Returns
    -------

    out: str
      The ID of the started pipeline.
        """
        cmd = ["curl",
               "-X", "POST",
               "--fail",
               "-F", f"token={self._config['gitlab_pipeline_token']}",
               "-F", "ref=ruqad",
               "https://gitlab.indiscale.com/api/v4/projects/268/trigger/pipeline"
               ]
        cmd_result = run(cmd, check=False, capture_output=True)
        result = json.loads(cmd_result.stdout)
        return str(result["id"])

    def _wait_for_check(self, pipeline_id: str) -> str:
        """Wait for the pipeline to finish successfully.

    Parameters
    ----------
    pipeline_id : str
      The pipeline ID to watch.

    Returns
    -------
    out : str
      The ID of the "report" job.  FIXME: or "pages"?
        """
        # Wait for pipeline to finish.
        cmd = [
            "curl",
            "--header", f"PRIVATE-TOKEN: {self._config['gitlab_api_token']}",
            f"https://gitlab.indiscale.com/api/v4/projects/268/pipelines/{pipeline_id}"
        ]
        while True:
            cmd_result = run(cmd, check=True, capture_output=True)
            result = json.loads(cmd_result.stdout)
            if result["status"] != "running" and result["finished_at"] is not None:
                break
            time.sleep(1)
        if not result["status"] == "success":
            print("Pipeline terminated unsuccessfully.")
            raise self.CheckFailed(result)

        # Get jobs.
        # We expect that these jobs are run runby the pipeline:
        # - evaluate: run the quality check
        # - report: build the report
        # - pages: publish the report (not relevant for us)
        cmd = [
            "curl",
            "--header", f"PRIVATE-TOKEN: {self._config['gitlab_api_token']}",
            f"https://gitlab.indiscale.com/api/v4/projects/268/pipelines/{pipeline_id}/jobs"
        ]
        cmd_result = run(cmd, check=False, capture_output=True)
        result = json.loads(cmd_result.stdout)
        evaluate_job = [job for job in result if job["name"] == "evaluate"][0]
        if not evaluate_job["status"] == "success":
            raise self.CheckFailed(result)
        report_job = [job for job in result if job["name"] == "report"][0]
        return report_job["id"]

    def _download_result(self, job_id: str, target_dir: str = "."):
        """Download the artifacts from the pipeline.

    Parameters
    ----------
    job_id : str
      The ID of the job with the artifacts.

    target_dir : str, default="."
      Download to this directory.
        """
        target = os.path.join(target_dir, "artifacts.zip")
        cmd = [
            "curl",
            "--location", "--fail",
            "--output", target,
            "--header", f"PRIVATE-TOKEN: {self._config['gitlab_api_token']}",
            f"https://gitlab.indiscale.com/api/v4/projects/268/jobs/{job_id}/artifacts"
        ]
        cmd_result = run(cmd, check=False, capture_output=True)
        assert cmd_result.returncode == 0
        print(f"Downloaded archive to: {target}")


def _parse_arguments():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(description='Trigger quality checks for the given content')
    parser.add_argument('-f', '--file', required=True,
                        help=("Check the quality for this file."),
                        )
    # FIXME needs both file and schema.

    return parser.parse_args()


def main():
    """The main function of this script."""
    args = _parse_arguments()
    qc = QualityChecker()
    qc.check(filename=args.file)


if __name__ == "__main__":
    main()
