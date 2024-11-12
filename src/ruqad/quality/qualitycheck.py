#!/usr/bin/env python3

# This file is a part of the RuQaD Project.
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
from subprocess import run

import boto3
import toml


def read_secrets() -> dict:
    """Read secrets from ``./qualitycheck_secrets.toml``.

This config file must define the following:

- ``pipeline_token``: To trigger a pipeline.
- ``api_token``: Project access token to access pipeline information.

Returns
-------
out: dict
  The secrets.
    """
    secrets = toml.load("./qualitycheck_secrets.toml")
    assert "pipeline_token" in secrets
    assert isinstance(secrets["pipeline_token"], str)
    assert "api_token" in secrets
    assert isinstance(secrets["api_token"], str)

    return secrets


class QualityChecker:

    class CheckFailed(RuntimeError):
        pass

    def __init__(self):
        """The QualityChecker can do quality checks for content.
        """
        self._bucketname = "testbucket"
        self._secrets = read_secrets()
        session = boto3.Session(aws_access_key_id=self._secrets["s3_access_key"],
                                aws_secret_access_key=self._secrets["s3_secret_key"])
        # FIXME no SSL during testing!
        self._s3_client = session.client("s3", endpoint_url=self._secrets["s3_endpoint_url"])

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
            print("Check failed")
            from IPython import embed
            embed()

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

    def _upload(self, filename: str):
        """Upload the file to the S3 bucket.

Parameters
----------
filename : str
  The file to be checked.
        """
        self._s3_client.upload_file(filename, self._bucketname, filename)

    def _trigger_check(self) -> str:
        """Trigger a new pipeline to start quality checks.

    Parameters
    ----------
    pipeline_token : str
        The token to trigger the pipeline.

    Returns
    -------

    out: str
      The ID of the started pipeline.
        """
        cmd = ["curl",
               "-X", "POST",
               "--fail",
               "-F", f"token={self._secrets['pipeline_token']}",
               "-F", "ref=main",
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
            "--header", f"PRIVATE-TOKEN: {self._secrets['api_token']}",
            f"https://gitlab.indiscale.com/api/v4/projects/268/pipelines/{pipeline_id}"
        ]
        while True:
            cmd_result = run(cmd, check=True, capture_output=True)
            result = json.loads(cmd_result.stdout)
            if result["finished_at"] is not None:
                break
            time.sleep(1)
        if not result["status"] == "success":
            print("Pipeline terminated unsuccessfully.")
            raise self.CheckFailed(result)

        # Get jobs.
        cmd = [
            "curl",
            "--header", f"PRIVATE-TOKEN: {self._secrets['api_token']}",
            f"https://gitlab.indiscale.com/api/v4/projects/268/pipelines/{pipeline_id}/jobs"
        ]
        cmd_result = run(cmd, check=False, capture_output=True)
        result = json.loads(cmd_result.stdout)
        evaluate_job = [job for job in result if job["name"] == "evaluate"][0]
        if not evaluate_job["status"] == "success":
            raise self.CheckFailed()
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
            "--header", f"PRIVATE-TOKEN: {self._secrets['api_token']}",
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
