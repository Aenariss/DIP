#
#  Copyright (C) 2020  Martin Bednar
#  Copyright (C) 2021  Matus Svancar
#  Copyright (C) 2024  Jana Petranova
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import pytest

from shared_set import get_shared_noaddon, get_shared_addonRun, get_shared_addonsInstalled, get_shared_browser, get_shared_level
import  values_expected 

## This module is automatically called by pytest before start executing tests.
#
#  It contains setup method that are called before tests executing.
#  Here is defined variables browser and expected that are given to tests as a parameter.


## Setup method. Provides shared browser, run without any extensions and run with extensions to all tests.
@pytest.fixture(scope="session", autouse=True)
def noaddon():
    return get_shared_noaddon()

@pytest.fixture(scope="session", autouse=True)
def addonRun():
    return get_shared_addonRun()

@pytest.fixture(scope="session", autouse=True)
def browser():
    return get_shared_browser()

## Setup method: expected provide expected values to all tests.

@pytest.fixture(scope="session", autouse=True)
def expected():
    addonsTested = get_shared_addonsInstalled()
    # The way the testing is set up right now is to always pick JShelter values as expected values if JShelter was tested in any setting.
    # This is to save space in the values_expected.py file but can be changed any time, just delete the following if statement.
    if "JS" in addonsTested:
        js_level = get_shared_level()
        exp = "JS_" + str(js_level)
        return getattr(values_expected, exp, None)
    else:
        return getattr(values_expected, addonsTested, None)

