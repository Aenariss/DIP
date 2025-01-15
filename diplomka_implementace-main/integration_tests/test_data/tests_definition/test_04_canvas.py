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
from shared_set import get_shared_addonRun

## Test canvas - if canvas is spoofed: Reading from canvas returns white image.
##
## This test fails in Google Chrome on JShelter level 3 - expected failure because of known bug:
## selenium.common.exceptions.JavascriptException: Message: javascript error:
## Failed to execute 'getRandomValues' on 'Crypto': parameter 1 is not of type 'ArrayBufferView'.
def test_canvas(addonRun, expected):
    if get_shared_addonRun().protectCanvas is None:
        pytest.skip("Canvas attributes not tested.")
    is_spoofed = addonRun.protectCanvas
    if is_spoofed == "ERROR":
        print("\nCan not read Canvas data.")
        assert False
    else:
        if expected.protectCanvas == True:
            assert is_spoofed ==  True
        else:
            assert is_spoofed ==  False

def test_getImageData(noaddon, addonRun, expected):
    if get_shared_addonRun().canvasImageData is None:
        pytest.skip("Canvas attributes not tested.")
    if addonRun.canvasImageData == "ERROR":
        print("\n getImageData error.")
        assert False
    else:
        if expected.canvasImageData == 'SPOOF VALUE':
            assert addonRun.canvasImageData != noaddon.canvasImageData
        else:
            assert addonRun.canvasImageData == noaddon.canvasImageData


def test_to_data_URL(noaddon, addonRun, expected):
    if get_shared_addonRun().canvasDataURL is None:
        pytest.skip("Canvas attributes not tested.")
    if addonRun.canvasDataURL == "ERROR":
        print("\n toDataURL error.")
        assert False
    else:
        if expected.canvasDataURL == 'SPOOF VALUE':
            assert addonRun.canvasDataURL != noaddon.canvasDataURL
        else:
            assert addonRun.canvasDataURL == noaddon.canvasDataURL


def test_to_blob(noaddon, addonRun, expected):
    if get_shared_addonRun().canvasBlob is None:
        pytest.skip("Canvas blob not tested.")
    if addonRun.canvasBlob == "ERROR":
        print("\n toBlob error.")
        assert False
    else:
        if expected.canvasBlob == 'SPOOF VALUE':
            assert addonRun.canvasBlob != noaddon.canvasBlob
        else:
            assert addonRun.canvasBlob == noaddon.canvasBlob

def test_is_point_in_path(addonRun, expected):
    if get_shared_addonRun().canvasPointPath is None:
        pytest.skip("Canvas attributes not tested.")
    if addonRun.canvasPointPath == "ERROR":
        print("\n isPointInPath error.")
        assert False
    else:
        if expected.canvasPointPath in {'SPOOF VALUE','FALSE VALUE'}:
            assert addonRun.canvasPointPath == False
        else:
            assert addonRun.canvasPointPath == True

def test_is_point_in_stroke(addonRun, expected):
    if get_shared_addonRun().canvasPointStroke is None:
        pytest.skip("Canvas attributes not tested.")
    if addonRun.canvasPointStroke == "ERROR":
        print("\n isPointInStroke error.")
        assert False
    else:
        if expected.canvasPointStroke in {'SPOOF VALUE','FALSE VALUE'} :
            assert addonRun.canvasPointStroke == False
        else:
            assert addonRun.canvasPointStroke == True