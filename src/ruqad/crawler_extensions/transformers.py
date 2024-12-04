# encoding: utf-8
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2024 Alexander Schlemmer <a.schlemmer@indiscale.com>
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

from typing import Any


def cast_metadata_type(in_value: Any, in_parameters: dict) -> Any:
    """
    Cast the type of `in_value` to the type given by in_parameters["out_type"]
    if the varname given by in_parameters["var_name"] equals in_parameters["var_value"].
    Just return the in_value otherwise.

    The type can be one of:
    float, int, bool, str
    """
    if "out_type" not in in_parameters:
        raise RuntimeError("Parameter `out_type` missing.")

    if "var_name" not in in_parameters:
        raise RuntimeError("Parameter `var_name` missing.")

    if "var_value" not in in_parameters:
        raise RuntimeError("Parameter `var_value` missing.")

    typedict = {
        "float": float, "int": int, "bool": bool, "str": str
    }

    out_type = in_parameters["out_type"]
    if out_type not in typedict.keys():
        raise RuntimeError("Parameter `out_type` can only be one of float, int, bool or str.")

    if in_parameters["var_name"] != in_parameters["var_value"]:
        return in_value

    return typedict[out_type](in_value)
