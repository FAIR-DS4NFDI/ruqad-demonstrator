#!/usr/bin/env python3

# This file is a part of the RuQaD project.
#
# Copyright (C) 2024 IndiScale GmbH <www.indiscale.com>
# Copyright (C) 2024 Henrik tom Wörden <h.tomwoerden@indiscale.com>
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

"""Daemon like script which monitors the Kadi4Mat server for new items.
"""

import traceback
import shutil
import os
import argparse
import sys
from time import sleep
from tempfile import TemporaryDirectory
from datetime import datetime, timezone

sys.path.append(os.path.dirname(__file__))

from qualitycheck import QualityChecker                           # NOQA
from kadi import collect_records_created_after, download_eln_for  # NOQA
from crawler import trigger_crawler                               # NOQA
from kadi_apy import KadiManager                                  # NOQA


KADIARGS = {
    "host": os.environ['KADIHOST'],
    "pat": os.environ['KADITOKEN']
}


if __name__ == "__main__":
    cut_off_date = datetime.fromisoformat("1990-01-01 02:34:42.484312+00:00")
    while True:
        try:
            timestamp = datetime.now(timezone.utc)
            with KadiManager(**KADIARGS) as manager:
                qc = QualityChecker()
                print(f"Checking for records created after {cut_off_date}...")
                rec_ids = collect_records_created_after(manager, cut_off_date)
                cut_off_date = timestamp

                if len(rec_ids) > 5:
                    print("skipping, too many recs: ", len(rec_ids))
                    continue
                if len(rec_ids) == 0:
                    print("no new recs")
                for rid in rec_ids:
                    with TemporaryDirectory() as cdir:
                        eln_file = os.path.join(cdir, "export.eln")
                        download_eln_for(manager, rid, path=eln_file)
                        print(f"Downlaoded {eln_file}")
                        qc.check(filename=eln_file, target_dir=cdir)
                        print(f"Quality check done. {os.listdir(cdir)}")
                        # trigger crawler on dir
                        remote_dir_path = os.path.join(cdir, "ruqad", str(rid))
                        os.makedirs(remote_dir_path)
                        shutil.move(os.path.join(cdir, "artifacts.zip"),
                                    os.path.join(remote_dir_path, "report.zip"))
                        shutil.move(os.path.join(cdir, "export.eln"),
                                    os.path.join(remote_dir_path, "export.eln"))
                        trigger_crawler(target_dir=cdir)
            sleep(60)

        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            print("ERROR")
            print(traceback.format_exc())
            print(e)
