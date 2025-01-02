#!/usr/bin/env python3
# Small module wrapping the crawler run call
# A. Schlemmer, 11/2024


import os
import sys
from importlib import resources
from os import walk
from os.path import join

import linkahead as db
from caoscrawler.crawl import crawler_main
from caoscrawler.scanner import scan_directory
from caoscrawler.validator import (load_json_schema_from_datamodel_yaml,
                                   validate)

ruqad_crawler_settings = resources.files('ruqad').joinpath('resources/crawler-settings')


def trigger_crawler(target_dir: str) -> tuple[bool, list[db.Entity]]:
    """
    Trigger a standard crawler run equivalent to the command line:

    ```
    caosdb-crawler -i crawler/identifiables.yaml -s update crawler/cfood.yaml <target_dir>
    ```

    Returns
    -------

    out: tuple[bool, list[db.Entity]]
      - 1st element of tuple: ``False`` in case of unsuccessful metadata validation
        and ``True`` otherwise.
      - 2nd element of tuple: list of quality check records.
    """

    # insert all .zip and .eln files, if they do not yet exist
    for fp, ds, fs in walk(target_dir):
        for fn in fs:
            if fn.endswith(".eln") or fn.endswith(".zip"):

                file_path = join(target_dir, fp, fn)
                file_entity = join(fp[len(target_dir):], fn)
                file_ent = db.File(file=file_path,
                                   path=file_entity)

                print(f"retrieve {join(fp, fn)}")
                file_ent.retrieve()
                if file_ent.id is None:
                    print(f"insert {join(fp, fn)}")
                    file_ent.insert()
                else:
                    print(f"update {join(fp, fn)}")
                    file_ent.update()
    print("meta data check")
    datamodel_yaml_file = ruqad_crawler_settings.joinpath('datamodel.yaml')
    schemas = load_json_schema_from_datamodel_yaml(datamodel_yaml_file)
    entities = scan_directory(target_dir,
                              ruqad_crawler_settings.joinpath('cfood.yaml'))

    ent_qc = []                 # Quality check result records

    # Show warning if license is not present in an eln file:
    for ent in entities:
        if not (len(ent.parents) == 1 and ent.parents[0].name == "QualityCheck"):
            continue
        ent_qc.append(ent)

        if not ent.get_property("FAIRLicenseCheck").value:
            print("{} does not contain a license.".format(ent.get_property("ELNFile").value.path))

    # Remove files from entities:
    records = [r for r in entities if r.role == "Record"]
    validation = validate(records, schemas)

    if not all([i[0] for i in validation]):
        print("Metadata validation failed. Validation errors:")
        for v, recordtype in zip(validation, schemas.keys()):
            if not v[0]:
                print("{}: {}".format(recordtype, v[1]))
        return (False, ent_qc)

    print("crawl", target_dir)
    crawler_main(crawled_directory_path=target_dir,
                 debug=True,
                 cfood_file_name=ruqad_crawler_settings.joinpath('cfood.yaml'),
                 identifiables_definition_file=ruqad_crawler_settings.joinpath(
                     'identifiables.yaml'),
                 remove_prefix="/"+os.path.basename(target_dir))

    return (True, ent_qc)
