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
tests the interaction with the Kadi API
"""
import os
from datetime import datetime
from tempfile import NamedTemporaryFile
import zipfile
from uuid import uuid1

from ruqad.kadi import collect_records_created_after, download_eln_for
from kadi_apy import KadiManager
from time import sleep

KADIARGS = {
    "host": "https://demo-kadi4mat.iam.kit.edu",
    "pat": os.environ['KADITOKEN']
}


def test_collect():
    """
    queries data from the Kadi demo instance and checks whether the cut-off date is used correctly
    """
    new1, new2, newest = None, None, None
    with KadiManager(**KADIARGS) as manager:
        query_params = {"per_page": 1, "sort": "-created_at"}
        newest = manager.search.search_resources("record", **query_params).json()["items"][0]
        cut_off_date = datetime.fromisoformat(newest["created_at"])
        new1 = manager.record(identifier=str(uuid1()), create=True)
        new2 = manager.record(identifier=str(uuid1()), create=True)
    sleep(15)
    with KadiManager(**KADIARGS) as manager:
        rec_ids = collect_records_created_after(manager, cut_off_date)
        known_new_recs = [int(newest["id"]), new1.id, new2.id]
        for knr in known_new_recs:
            assert knr in rec_ids
        known_old_recs = [158, newest["id"]-1, 1]
        for knr in known_old_recs:
            assert knr not in rec_ids


def test_download():
    """ downloads a record from the demo instance and checks that the download occurred correctly"""
    temp = NamedTemporaryFile(delete=False)
    temp.close()
    with KadiManager(**KADIARGS) as manager:
        download_eln_for(manager, 664, temp.name)
    assert os.path.getsize(temp.name) > 0
    assert zipfile.is_zipfile(temp.name)
