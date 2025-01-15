#
#  Copyright (C) 2022  Martin Bednar
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

from math_operations import is_in_accuracy
from shared_set import get_shared_addonRun

import pytest

## Test time accuracy.
def test_accuracy(addonRun, expected):
    if get_shared_addonRun().time is None:
        pytest.skip("Time  not tested.")
    #Suppose time is rounded.
    is_time_rounded = True
    time = addonRun.time
    # Make 3 measurement.
    for t in time:
        # Wait a while to value of time will be changed.
        if expected.time['accuracy'] == 'EXACTLY':
            if int(t / 10) * 10 != t:
                # miliseconds was not rounded. At least one of three measurement has to say value was not rounded.
                is_time_rounded = False
        else:
            assert is_in_accuracy(t, expected.time['accuracy'])
 
    if expected.time['accuracy'] == 'EXACTLY':
        # At least one of three measurement has to say value was not rounded.
        # is_time_rounded should be false if EXACTLY value is required.
        assert not is_time_rounded
