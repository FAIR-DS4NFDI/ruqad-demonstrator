# Copyright (C) 2024 IndiScale GmbH <info@indiscale.com>
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
#

"""
utilities to create .eln exports for certain records hosted in a Kadi instance
"""
from __future__ import annotations
from kadi_apy import KadiManager
from datetime import datetime

PAGE_SIZE = 100

def _generate_pages(manager)->dict:
    """
    Generates JSON responses (dict) that represent single pages returned by the Kadi API

    Paremters
    ---------
    manager: KadiManager, KadiManager instance used to connect to the Kadi API

    Returns
    -------
        dict, the JSON response as dict
    """
    query_params = {"per_page":PAGE_SIZE, "sort": "-created_at"}
    # test search to get number of pages.
    response = manager.search.search_resources("record", **query_params).json()
    n_pages = response["_pagination"]["total_pages"]
    for ii in range(n_pages):
        query_params.update({"page":ii+1})
        yield manager.search.search_resources("record", **query_params).json()


def collect_records_created_after(manager: KadiManager, cut_off_date: datetime.datetime)->list(int):
    """
    Iterates page-wise over the responses of the Kadi API until records are reached that are older
    than the given cut_off_date.

    Paremters
    ---------
    manager: KadiManager, KadiManager instance used to connect to the Kadi API
    cut_off_date: datetime, Records that were created after this date are included in the returned
                 list

    Returns
    -------
        list(int), list of IDs of records that were created after the given cut_off_date
    """
    record_ids = []
    done = False
    for response in _generate_pages(manager):
        for el in response["items"]:
            if cut_off_date > datetime.fromisoformat(el["created_at"]):
                done = True
                break
            record_ids.append(el["id"])
        if done:
            break
    return record_ids

def download_eln_for(manager: KadiManager, rid: int, path: str) -> None:
    """
    Downloads the record with the given ID as '.eln' file and stores it in the given path.

    Paremters
    ---------
    manager: KadiManager, KadiManager instance used to connect to the Kadi API
    rid: int, ID of the record to be exported
    path: str, the path where the file will be stored
    """
    rec = manager.record(id=rid)
    rec.export(path=path, export_type='ro-crate')

def main():
    with KadiManager(instance='demo') as manager:
        cut_off_date = datetime.fromisoformat("2024-10-01 02:34:42.484312+00:00")
        rec_ids = collect_records_created_after(manager, cut_off_date)
        print(rec_ids)


if __name__ == "__main__":
    main()
