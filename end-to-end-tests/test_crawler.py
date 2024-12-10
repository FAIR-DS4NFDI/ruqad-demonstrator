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
tests the crawling of ELN files
"""
import os
import re
from pathlib import Path

from ruqad.crawler import trigger_crawler

DATADIR = Path(__file__).parent / "data" / "crawler_data"


def test_crawl():
    """
    crawl a directory as it would be created by export from kadi and running a data quality check
    """
    print(os.listdir(DATADIR))
    retval, ent_qc = trigger_crawler(os.fspath(DATADIR))

    # Check that validation of metadata was successful:
    assert retval

    # Check that license was present in 1223 and absent in 1222:
    qc = {}
    for ent in ent_qc:
        pth = ent.get_property("ELNFile").value.path
        match = re.match("/.*/.*/(?P<folder>[0-9]+)/.*\.eln", pth)
        assert match is not None
        qc[match.group("folder")] = ent

    assert qc["1223"].get_property("FAIRLicenseCheck").value
    assert not qc["1222"].get_property("FAIRLicenseCheck").value
