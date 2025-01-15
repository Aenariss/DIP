#
#  Copyright (C) 2021  Martin Bednar
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


from shared_set import get_shared_addonRun
import pytest

## Test methods.toString(). They should be always unchanged by JShelter.
def test_methods_toString(noaddon, addonRun):
    if get_shared_addonRun().methods_toString is None:
        pytest.skip("Methods to string not tested.")
    for method in addonRun.methods_toString:
        assert addonRun.methods_toString[method] == noaddon.methods_toString[method]
