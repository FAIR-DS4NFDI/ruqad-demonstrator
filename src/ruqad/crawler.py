#!/usr/bin/env python3
# Small module wrapping the crawler run call
# A. Schlemmer, 11/2024


from importlib import resources
from os import walk
from os.path import join, sep
from pathlib import Path

import linkahead as db
from caoscrawler.crawl import crawler_main

ruqad_crawler_settings = resources.files('ruqad').joinpath('resources/crawler-settings')


def trigger_crawler(target_dir: str):
    """
    Trigger a standard crawler run equivalent to the command line:

    ```
    caosdb-crawler -i crawler/identifiables.yaml -s update crawler/cfood.yaml <target_dir>
    ```
    """

    # insert all .zip and .eln files, if they do not yet exist
    for fp, ds, fs in walk(target_dir):
        for fn in fs:
            if fn.endswith(".eln") or fn.endswith(".zip"):
                file_ent = db.File(file=join(fp, fn),
                                   path=join(*(fp.split(sep)[1:]), fn))
                print(f"retrieve {join(fp,fn)}")
                file_ent.retrieve()
                if file_ent.id is None:
                    print(f"insert {join(fp,fn)}")
                    file_ent.insert()
                else:
                    print(f"update {join(fp,fn)}")
                    file_ent.update()

    print("crawl", target_dir)
    crawler_main(crawled_directory_path=target_dir,
                 cfood_file_name=ruqad_crawler_settings.joinpath('cfood.yaml'),
                 identifiables_definition_file=ruqad_crawler_settings.joinpath('identifiables.yaml'),
                 remove_prefix="/" + target_dir[:-1])
