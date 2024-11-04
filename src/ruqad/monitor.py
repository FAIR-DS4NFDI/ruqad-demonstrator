"""
monitor the kadi instance
"""
import os
from time import sleep
from tempfile import NamedTemporaryFile
import traceback
from datetime import datetime, timezone
from kadi_apy import KadiManager

from .kadi import collect_records_created_after, download_eln_for


KADIARGS = {
    "host": os.environ['KADIHOST'],
    "pat": os.environ['KADITOKEN']
}


if __name__ == "__main__":
    cut_off_date = datetime.fromisoformat("1990-01-01 02:34:42.484312+00:00")
    while True:
        try:
            timestamp  = datetime.now(timezone.utc)
            with KadiManager(**KADIARGS) as manager:
                print(f"Checking for records created after {cut_off_date}...")
                rec_ids = collect_records_created_after(manager, cut_off_date)
                cut_off_date = timestamp

                if len(rec_ids)>5:
                    print("skipping, too many recs: ", len(rec_ids))
                    continue
                if len(rec_ids)==0:
                    print("no new recs")
                for rid in rec_ids:
                    temp = NamedTemporaryFile(delete=False)
                    temp.close()
                    download_eln_for(manager, rid, path= temp.name)
                    print(temp.name)
            sleep(5)

        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            print("ERROR")
            print(traceback.format_exc())
            print(e)
