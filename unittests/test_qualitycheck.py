# Copyright (C) 2024 IndiScale GmbH <info@indiscale.com>
# Copyright (C) 2024 Daniel Hornung <d.hornung@indiscale.com>
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

"""Unit tests for the QualityChecker."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock

from ruqad import qualitycheck


@patch("boto3.Session.client")
def test_qc_internal(mock_s3_client):
    zipfile = (Path(__file__).parents[1] / "end-to-end-tests" / "data" / "crawler_data" / "ruqad" /
               "1223" / "export.eln")
    qc = qualitycheck.QualityChecker()
    qc._extract_content(zipfile, upload=True)
    correct_call = False
    for call in mock_s3_client.mock_calls:
        if not call[0] == '().upload_file':
            continue
        if (len(call.args) == 3
            and call.args[0].endswith("abalone2.csv")
            and call.args[1] == "ruqad"
            and call.args[2] ==
                "data/test-crawler-second/test-crawler-second/files/abalone2.csv"):
            correct_call = True
            break
    assert correct_call
