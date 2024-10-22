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
from ruqad import kadi
from datetime import datetime
from unittest.mock import patch, Mock

def mock_generator(manager):
    """ Mocks the server response. We only need the keys: "items", "created_at", and "id"."""
    pages = [
        {"items": [
            {"created_at": "2024-01-02 01:00:00.000000+00:00",
             "id": 1},
            {"created_at": "2024-01-02 01:00:00.000000+00:00",
             "id": 2}
        ]},{"items": [
            {"created_at": "2024-01-01 01:00:00.000000+00:00",
             "id": 3},
            {"created_at": "2024-01-01 01:00:00.000000+00:00",
             "id": 4}
        ]}
    ]
    for el in pages:
        yield el


@patch("ruqad.kadi._generate_pages", new=Mock(side_effect=mock_generator))
def test_collect_records_created_after():
    # we set a cut of date after half of the records and check that we get the correct ids
    assert [1,2]==kadi.collect_records_created_after(manager=None,
                                       cut_of_date= datetime.fromisoformat(
                                            "2024-01-01 03:00:00.000000+00:00")
                                       )
