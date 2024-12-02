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
from pathlib import Path

from ruqad.crawler import trigger_crawler

DATADIR = Path(__file__).parent / "data" / "crawler_data"


def test_crawl():
    """
    crawl a directory as it would be created by export from kadi and running a data quality check
    """
    print(os.listdir(DATADIR))
    retval = trigger_crawler(os.fspath(DATADIR))
    assert retval
