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

from ruqad.kadi import collect_records_created_after, download_eln_for
from kadi_apy import KadiManager

KADIARGS = {
    "host": "https://demo-kadi4mat.iam.kit.edu",
    "pat": os.environ['KADITOKEN']
}

def test_collect():
    """
    queries data from the Kadi demo instance and checks whether the cut of date is used correctly
    """
    with KadiManager(**KADIARGS) as manager:
        cut_of_date = datetime.fromisoformat("2024-10-01 02:34:42.484312+00:00")
        rec_ids = collect_records_created_after(manager, cut_of_date)
        assert (rec_ids ==[664, 656, 641, 640, 639, 638, 637],
                "when the sample data changes, this test may fail")

def test_download():
    """ downloads a record from the demo instance and checks that the download occured correctly"""
    temp  = NamedTemporaryFile(delete=False)
    temp.close()
    with KadiManager(**KADIARGS) as manager:
        download_eln_for(manager, 664, temp.name)
    assert os.path.getsize(temp.name)>0
    assert zipfile.is_zipfile(temp.name)
