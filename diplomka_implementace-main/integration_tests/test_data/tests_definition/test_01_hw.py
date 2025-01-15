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

import pytest
from shared_set import get_shared_addonRun

## Test device memory.
def test_device_memory(noaddon, addonRun, expected, browser):
	if get_shared_addonRun().device.deviceMemory is None:
		pytest.skip("Device attributes not tested.")
	if noaddon.device.deviceMemory == "null" and addonRun.device.deviceMemory == "null":
		return # This browser does not support deviceMemory so JShelter should not spoof that value
	elif noaddon.device.deviceMemory == "null":
		assert addonRun.device.deviceMemory == "null"
	if expected.device.deviceMemory[browser] == 'SPOOF VALUE':
		assert addonRun.device.deviceMemory in expected.device.deviceMemory['valid_values']
		assert addonRun.device.deviceMemory <= noaddon.device.deviceMemory
	else:
		assert addonRun.device.deviceMemory == noaddon.device.deviceMemory


## Test hardware concurrency.
def test_hardware_concurrency(noaddon, addonRun, expected):
	if get_shared_addonRun().device.hardwareConcurrency is None:
		pytest.skip("Device attributes not tested.")
	if expected.device.hardwareConcurrency['value'] == 'REAL VALUE':
		assert addonRun.device.hardwareConcurrency == noaddon.device.hardwareConcurrency
	elif expected.device.hardwareConcurrency['value'] == 'SPOOF VALUE':
		expectedval = expected.device.hardwareConcurrency['valid_values']
		if expectedval == "UP TO REAL VALUE":
			expectedval = range(noaddon.device.hardwareConcurrency + 1)
		assert addonRun.device.hardwareConcurrency in expectedval
	else:
		assert False # We should not get here


## Test IOdevices.
def test_IOdevices(noaddon, addonRun, expected):
	if get_shared_addonRun().device.IOdevices is None:
		pytest.skip("Device attributes not tested.")
	if expected.device.IOdevices == 'REAL VALUE':
		assert len(addonRun.device.IOdevices) == len(noaddon.device.IOdevices)
		for i in range(len(addonRun.device.IOdevices)):
			assert addonRun.device.IOdevices[i]['kind'] == noaddon.device.IOdevices[i]['kind']
	elif expected.device.IOdevices == 'EMPTY':
		if addonRun.device.IOdevices == 'ERROR':
			assert addonRun.device.IOdevices == 'ERROR'
		else:
			assert addonRun.device.IOdevices == []
			assert len(addonRun.device.IOdevices) == 0
	else:
		assert len(addonRun.device.IOdevices) in expected.device.IOdevices
