"""
monitor the kadi instance
"""
import os
import shutil
import traceback
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from time import sleep

from kadi_apy import KadiManager

from .crawler import trigger_crawler
from .kadi import collect_records_created_after, download_eln_for
from .qualitycheck import QualityChecker

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
                        remote_dir_path= os.path.join(cdir, "ruqad", str(rid))
                        os.makedirs(remote_dir_path)
                        shutil.move(os.path.join(cdir, "artifacts.zip"),
                                    os.path.join(remote_dir_path, "quality_report.zip"))
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
