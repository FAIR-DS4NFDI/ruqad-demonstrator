"""
Tests CPU and Memory usage of RuQaD
"""
import cProfile, pstats, io
from pstats import SortKey
from time import sleep,time
from tempfile import TemporaryDirectory
from datetime import datetime, timezone
from pathlib import Path

from memory_profiler import profile as mprofile

from ruqad.qualitycheck import QualityChecker
from ruqad.kadi import collect_records_created_after, download_eln_for, KadiManager
from ruqad.crawler import trigger_crawler
import os
import shutil
from memory_profiler import memory_usage

SKIP_QUALITY_CHECK = os.getenv("SKIP_QUALITY_CHECK") is not None
KADIARGS = {
    "host": os.environ['KADIHOST'],
    "pat": os.environ['KADITOKEN'],
}

"""
call this file to check memory and cpu usage of the RuQaD demonstrator
"""

def _run(n=-1):
    cut_off_date = datetime.fromisoformat("1990-01-01 02:34:42.484312+00:00")
    with KadiManager(**KADIARGS) as manager:
        print(f"Checking for records created after {cut_off_date}...")
        rec_ids = collect_records_created_after(manager, cut_off_date)

        if len(rec_ids) == 0:
            print("no new recs")
        if n!=-1:
            rec_ids = rec_ids[:n]
        for rid in rec_ids:
            with TemporaryDirectory(delete=False) as cdir:
                eln_file = os.path.join(cdir, "export.eln")
                download_eln_for(manager, rid, path=eln_file)
                print(f"Downlaoded {eln_file}")
                if SKIP_QUALITY_CHECK:
                    print("Found env 'SKIP_QUALITY_CHECK', skipping quality check")
                else:
                    qc = QualityChecker()
                    qc.check(filename=eln_file, target_dir=cdir)
                    print(f"Quality check done. {os.listdir(cdir)}")
                # trigger crawler on dir
                remote_dir_path = os.path.join(cdir, "ruqad", str(rid))
                os.makedirs(remote_dir_path)
                if os.path.exists(os.path.join(cdir, "artifacts.zip")):
                    shutil.move(os.path.join(cdir, "artifacts.zip"),
                                os.path.join(remote_dir_path, "report.zip"))
                #else:
                #    Path(os.path.join(remote_dir_path, "report.zip")).touch()
                shutil.move(os.path.join(cdir, "export.eln"),
                            os.path.join(remote_dir_path, "export.eln"))
                trigger_crawler(target_dir=cdir)

def test_memory():
    # test that maximum memory usage is below 1GB
    assert 1000>max(memory_usage((_run, [10], {})))

def test_cpu():
    pr = cProfile.Profile()
    pr.enable()
    _run(n=1)
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(s.getvalue())
    ps.print_stats("ruqad", 10)
    ps.print_stats("crawler", 10)
    print(s.getvalue())

def test_runtime_eln_download():
    cut_off_date = datetime.fromisoformat("1990-01-01 02:34:42.484312+00:00")
    with KadiManager(**KADIARGS) as manager:
        rec_ids = collect_records_created_after(manager, cut_off_date)

        if len(rec_ids) == 0:
            print("no new recs")
        with TemporaryDirectory(delete=False) as cdir:
            eln_file = os.path.join(cdir, "export.eln")
            start = time()
            download_eln_for(manager, rec_ids[0], path=eln_file)
            stop = time()

    print(f"time for downloading eln: {stop-start:.2f} s")

def test_runtime_crawler():
    cut_off_date = datetime.fromisoformat("1990-01-01 02:34:42.484312+00:00")
    with KadiManager(**KADIARGS) as manager:
        rec_ids = collect_records_created_after(manager, cut_off_date)

        if len(rec_ids) == 0:
            print("no new recs")
        with TemporaryDirectory(delete=False) as cdir:
            eln_file = os.path.join(cdir, "export.eln")
            download_eln_for(manager, rec_ids[0], path=eln_file)
            # trigger crawler on dir
            remote_dir_path = os.path.join(cdir, "ruqad", str(rec_ids[0]))
            os.makedirs(remote_dir_path)
            shutil.move(os.path.join(cdir, "export.eln"),
                        os.path.join(remote_dir_path, "export.eln"))
            start = time()
            trigger_crawler(target_dir=cdir)
            stop = time()

    print(f"time for crawling eln: {stop-start:.2f} s")

if __name__ == "__main__":
    test_memory()
    test_runtime_eln_download()
    test_cpu()
    test_runtime_crawler()
