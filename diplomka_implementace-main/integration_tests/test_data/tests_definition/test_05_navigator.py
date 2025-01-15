#
#  Copyright (C) 2021  Matus Svancar
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

import pytest
from shared_set import get_shared_addonRun

## Test user agent.
def test_user_agent(noaddon, addonRun, browser, expected):
    if get_shared_addonRun().navigator.userAgent is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.userAgent[browser] == 'REAL VALUE':
        assert addonRun.navigator.userAgent == noaddon.navigator.userAgent
    else:
        assert addonRun.navigator.userAgent == expected.navigator.userAgent[browser]

def test_app_version(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.appVersion is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.appVersion == 'REAL VALUE':
        assert addonRun.navigator.appVersion == noaddon.navigator.appVersion
    else:
        assert addonRun.navigator.appVersion == expected.navigator.appVersion

	
def test_platform(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.platform is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.platform == 'REAL VALUE':
        assert addonRun.navigator.platform == noaddon.navigator.platform
    else:
        assert addonRun.navigator.platform == expected.navigator.platform

def test_vendor(noaddon, addonRun, browser, expected):
    if get_shared_addonRun().navigator.vendor is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.vendor[browser] == 'REAL VALUE':
        assert addonRun.navigator.vendor == noaddon.navigator.vendor
    else:
        assert addonRun.navigator.vendor == expected.navigator.vendor[browser]

def test_language(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.language is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.language  == 'REAL VALUE':
        assert addonRun.navigator.language == noaddon.navigator.language 
    else:
        assert addonRun.navigator.language == expected.navigator.language 

def test_languages(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.languages is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.languages  == 'REAL VALUE':
        assert addonRun.navigator.languages == noaddon.navigator.languages 
    else:
        assert addonRun.navigator.languages == expected.navigator.languages 

def test_cookie_enabled(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.cookieEnabled is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.cookieEnabled  == 'REAL VALUE':
        assert addonRun.navigator.cookieEnabled == noaddon.navigator.cookieEnabled 
    else:
        assert addonRun.navigator.cookieEnabled == expected.navigator.cookieEnabled 

def test_do_not_track(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.doNotTrack is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.doNotTrack == 'REAL VALUE':
        assert addonRun.navigator.doNotTrack == noaddon.navigator.doNotTrack  
    else:
        assert addonRun.navigator.doNotTrack == expected.navigator.doNotTrack 

def test_oscpu(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.oscpu is None:
        pytest.skip("Navigator attributes not tested.")
    if expected.navigator.oscpu == 'REAL VALUE':
        assert addonRun.navigator.oscpu == noaddon.navigator.oscpu   
    else:
        assert addonRun.navigator.oscpu == expected.navigator.oscpu  

	
LIVING_STANDARD_PLUGINS = [
            {'description': 'Portable Document Format', 'filename': 'internal-pdf-viewer', 'name': 'PDF Viewer'},
            {'description': 'Portable Document Format', 'filename': 'internal-pdf-viewer', 'name': 'Chrome PDF Viewer'},
            {'description': 'Portable Document Format', 'filename': 'internal-pdf-viewer', 'name': 'Chromium PDF Viewer'},
            {'description': 'Portable Document Format', 'filename': 'internal-pdf-viewer', 'name': 'Microsoft Edge PDF Viewer'},
            {'description': 'Portable Document Format', 'filename': 'internal-pdf-viewer', 'name': 'WebKit built-in PDF'},
        ]

	
def test_plugins_count(noaddon, addonRun, browser, expected):
    if get_shared_addonRun().navigator.plugins is None:
        pytest.skip("Navigator attributes not tested.")
    if addonRun.navigator.plugins == LIVING_STANDARD_PLUGINS and noaddon.navigator.plugins == LIVING_STANDARD_PLUGINS:
        return # JShelter should not modify the plugins that are the same in all conformant browsers
    if expected.navigator.plugins['count'][browser] == 'IGNORE':
        return
    elif expected.navigator.plugins['count'][browser] == 'REAL VALUE':
        assert len(addonRun.navigator.plugins) == len(noaddon.navigator.plugins)
    elif expected.navigator.plugins['count'][browser] == 'PLUS_2':
        assert len(addonRun.navigator.plugins) == len(noaddon.navigator.plugins) + 2
    else:
        assert len(addonRun.navigator.plugins) == expected.navigator.plugins['count'][browser]

	
def test_plugins(noaddon, addonRun, browser, expected):
    if get_shared_addonRun().navigator.plugins is None:
        pytest.skip("Navigator attributes not tested.")
    if addonRun.navigator.plugins == LIVING_STANDARD_PLUGINS and noaddon.navigator.plugins == LIVING_STANDARD_PLUGINS:
        return # JShelter should not modify the plugins that are the same in all conformant browsers
    if expected.navigator.plugins['count'][browser] == 'IGNORE':
        return
    elif expected.navigator.plugins['count'][browser] == 'REAL VALUE':
        assert addonRun.navigator.plugins == noaddon.navigator.plugins
    elif expected.navigator.plugins['value'][browser] == 'EMPTY':
        assert not addonRun.navigator.plugins
    else:
        assert addonRun.navigator.plugins != noaddon.navigator.plugins

	
LIVING_STANDARD_MIME_TYPES = [
            {'description': 'Portable Document Format', 'enabledPlugin': 'PDF Viewer', 'suffixes':
             'pdf', 'type': 'application/pdf'},
            {'description': 'Portable Document Format', 'enabledPlugin': 'PDF Viewer', 'suffixes':
             'pdf', 'type': 'text/pdf'},
        ]

def test_mime_types(noaddon, addonRun, expected):
    if get_shared_addonRun().navigator.mimeTypes is None:
        pytest.skip("Navigator attributes not tested.")
    if addonRun.navigator.mimeTypes == LIVING_STANDARD_MIME_TYPES and noaddon.navigator.mimeTypes == LIVING_STANDARD_MIME_TYPES:
        return # JShelter should not modify the plugins that are the same in all conformant browsers
    if expected.navigator.mimeTypes == 'IGNORE':
        return
    elif expected.navigator.mimeTypes == 'EMPTY':
        assert addonRun.navigator.mimeTypes == []
    elif expected.navigator.mimeTypes == 'SPOOF VALUE':
        if noaddon.navigator.mimeTypes == []:
            assert addonRun.navigator.mimeTypes == []
        else:
            assert addonRun.navigator.mimeTypes != noaddon.navigator.mimeTypes
    else:
        assert addonRun.navigator.mimeTypes == noaddon.navigator.mimeTypes


## Test app version.
