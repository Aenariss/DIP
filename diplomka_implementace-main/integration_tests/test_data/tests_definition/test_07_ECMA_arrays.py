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


from shared_set import get_shared_browser, get_shared_addonRun
import pytest


def test_crypto_getRandomValues(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    random_crypto_values = addonRun.ECMAarrays['cryptoGetRandomValues']

    for array_type in random_crypto_values:
        nums = random_crypto_values[array_type]
        if len(nums) > 0:
            assert nums['0'] != nums['1'] or nums['0'] != nums['2'] or  nums['0'] != nums['3'] # It is highly unlikely that all three numbers are the same
            assert nums['1'] != nums['0'] or nums['1'] != nums['2'] or  nums['1'] != nums['3'] # It is highly unlikely that all three numbers are the same
            assert nums['2'] != nums['0'] or nums['2'] != nums['1'] or  nums['2'] != nums['3'] # It is highly unlikely that all three numbers are the same
            assert nums['3'] != nums['0'] or nums['3'] != nums['1'] or  nums['3'] != nums['2']
        else:
            pytest.fail("No random value generated (%s). Probable JavaScript error: Crypto.getRandomValues: Argument 1 does not implement interface ArrayBufferView." + array_type)

def test_ArrayBufferViews(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['arrayBufferViews']
    for array in arrays:
        assert arrays[array] == True
	
def test_TypedArraysInit(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysInt'] == True

def test_TypedArraysParams32(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['typedArraysParams32']
    for array in arrays:
        assert arrays[array] == True
	
def test_TypedArraysInitByLength(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysInitByLenght'] == True

def test_TypedArraysOverwriteElement(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysOverwriteElement'] == True

def test_TypedArraysOverwriteFull(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysOverwriteFull'] == True 

def test_TypedArraysParams8(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['typedArraysParams8']
    for array in arrays:
        assert arrays[array] == True

def test_TypedArrayFromBuffer(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['typedArrayFromBuffer']
    for array in arrays:
        assert arrays[array] == True

def test_TypedArraysMethods_set(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsSet'] == True

def test_TypedArraysMethods_reverse(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsReverse'] == True

def test_TypedArraysMethods_sort(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsSort'] == True

def test_TypedArraysMethods_fill(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsFill'] == True

def test_TypedArraysMethods_copyWithin(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsCopyWithin'] == True

def test_TypedArraysMethods_subarray(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['typedArrayMethodsSubarray']
    for array in arrays:
        assert arrays[array] == True
	
def test_TypedArraysMethods_slice(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['typedArraysMethodsSlice']
    for array in arrays:
        assert arrays[array] == True

def test_TypedArraysMethods_map(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsMap'] == True

def test_TypedArraysMethods_filter(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArrayMethodsFilter'] == True

def test_TypedArraysMethods_reduce(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArrayMethodsReduce'] == True

def test_TypedArraysMethods_reduceR(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsReduceR'] == True

def test_TypedArraysMethods_lastIndexOf(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsLastIndexOf'] == True

def test_TypedArraysMethods_forEach(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsForEach'] == True

def test_TypedArraysMethods_find(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsFind'] == True
	
def test_TypedArraysMethods_join(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArraysMethodsJoin'] == True
	
def test_TypedArraysMethods_entrieskeysvalues(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['typedArraysMethodsEntriesKeysValues']
    for array in arrays:
        assert arrays[array] == True
	
def test_TypedArraysMethods_from(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['typedArrayMethodsFrom'] == True

def test_DataViewInit(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['dataViewInit']
    for array in arrays:
        assert arrays[array] == True

def test_DataViewAccessors(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    arrays = addonRun.ECMAarrays['dataViewAccessors']
    for array in arrays['loopSetGet']:
        assert array == True
    assert arrays['floatSet'] == True
    assert arrays['intSet'] == True
    assert arrays['bigSet'] == True

def test_OneBufferMoreViews(addonRun):
    if get_shared_addonRun().ECMAarrays is None:
        pytest.skip("ECMA arrays not tested.")
    assert addonRun.ECMAarrays['oneBufferMoreViews'] == True

def test_worker_basic(addonRun, expected):
    if "chrome" in get_shared_browser():
        pytest.xfail("See https://pagure.io/JShelter/webextension/issue/80")
    if get_shared_addonRun().worker is None:
        pytest.skip("ECMA arrays not tested.")
    if expected.worker == "REMOVED":
        assert addonRun.worker['workerBasics']['isWorkerRemoved'] == True
        return
    assert addonRun.worker['workerBasics']['onMessage'] == True
    assert addonRun.worker['workerBasics']['onError'] == True
    assert addonRun.worker['workerBasics']['onMessageError'] == True
    assert addonRun.worker['workerBasics']['eventListener'] == True
    assert addonRun.worker['workerBasics']['postMessage'] == True
    assert addonRun.worker['workerBasics']['removeEventListener'] == True
    assert addonRun.worker['workerBasics']['terminate'] == True

'''
def test_worker_implements_dispatchEvent(addonRun):
    assert addonRun.worker['workerImplementsDispatchEvent'] == True

def test_worker_check_communication_handler(addonRun):
    assert addonRun.worker['workerCheckCommunicationHandler'] == True

def test_worker_error(addonRun):
    assert addonRun.worker['workerError'] == True

def test_worker_check_communication_listener(addonRun):
    assert addonRun.worker['workerCheckCommunicationListener'] == True


def test_worker_terminate(addonRun):
    assert addonRun.worker['workerTerminate'] == True

def test_worker_dispatchEvent(addonRun):
    assert addonRun.worker['workerDispatchEvent'] == True
'''
