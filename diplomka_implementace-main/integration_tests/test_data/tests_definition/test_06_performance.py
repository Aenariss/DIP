#
#  Copyright (C) 2020  Martin Bednar
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

import pytest
from shared_set import get_shared_addonRun

## Test performance.
def test_performance(addonRun, expected):
    if get_shared_addonRun().performance is None:
        pytest.skip("Performance  not tested.")
    is_performance_rounded = True
    performance = addonRun.performance
    # Make 3 measurement.
    for i in performance:
        # Wait a while to value of performance will be changed.
        if expected.performance['accuracy'] == 'EXACTLY':
            if int(i / 10) * 10 != i:
                # Performance was not rounded. At least one of three measurement has to say value was not rounded.
                is_performance_rounded = False
        else:
            assert is_in_accuracy(i, expected.performance['accuracy'])

    if expected.performance['accuracy'] == 'EXACTLY':
        # At least one of three measurement has to say value was not rounded.
        # is_performance_rounded should be false if EXACTLY value is required.
        assert not is_performance_rounded
