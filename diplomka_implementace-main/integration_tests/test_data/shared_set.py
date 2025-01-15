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

## During testing multiple runs can be tested.
#  Variable _shared_browser is for testing all runs in one browser.
#  Variable _noaddon represents attribute values calculated while no extension was installed.
#  Variable _addonRun represents attribute values calculated while a combination of extensions was installed.
#  Variable _level is set if JShelter was installed and represents selected testing level.
#  Variable _addonsInstalled is a list of extensions installed during the tested visit.

_noaddon = None
_addonRun = None
_level = None
_browser = None
_addonsInstalled = None


## Setter for _shared_browser.
def set_shared_noaddon(noaddon):
    global _noaddon
    _noaddon = noaddon

def set_shared_addonRun(addonRun):
    global _addonRun
    _addonRun = addonRun

def set_shared_level(level):
    global _level
    _level = level

def set_shared_browser(browser):
    global _browser
    _browser = browser

def set_shared_addonsInstalled(addonsInstalled):
    global _addonsInstalled
    _addonsInstalled = addonsInstalled

def get_shared_noaddon():
    global _noaddon
    return _noaddon   

def get_shared_addonRun():
    global _addonRun
    return _addonRun

def get_shared_level():
    global _level
    return int(_level)

def get_shared_browser():
    global _browser
    return str(_browser)

def get_shared_addonsInstalled():
    global _addonsInstalled
    return str(_addonsInstalled)
