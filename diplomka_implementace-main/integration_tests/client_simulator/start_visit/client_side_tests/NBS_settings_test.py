#
#  JShelter is a browser extension which increases level
#  of security, anonymity and privacy of the user while browsing the
#  internet.
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
	
from time import sleep

def switch_NBS_setting(driver, options_page):
    driver.get(options_page.replace("/options.html", "/popup.html"))
    sleep(1)
    driver.find_elements("class name", 'slider')[1].click()
    sleep(1)
 
def get_NBS_setting(driver, options_page):
    driver.get(options_page.replace("/options.html", "/popup.html"))
    sleep(2)
    return(driver.execute_script("return window.getComputedStyle(document.querySelector('#nbs_whitelist .switch_wrapper .switch .slider'),':before').getPropertyValue('content')"))

def test_switching_NBS(driver, options_page, browser_type):
    if "chrome" in browser_type:
        # Not able to test NBS switch in Google Chrome.
        # Can not show popup.html in Chrome. Popup.html is not accesible and testable.
        return
    NBS_setting_values = ['"ON"', '"OFF"']
    
    original_setting = get_NBS_setting(driver, options_page)
    original_setting_index = NBS_setting_values.index(original_setting)
    
    # Range is saing how many times should NBS be switched.
    for i in range(4):
        switch_NBS_setting(driver, options_page)
        if get_NBS_setting(driver, options_page) == NBS_setting_values[(i + 1 + original_setting_index) % 2]:
            print("Testing Network Boundary Shield settings succesfull.")
        else:
            print("Testing Network Boundary Shield settings failed.")
    
    # Return original value
    if get_NBS_setting(driver, options_page) != original_setting:
        switch_NBS_setting(driver, options_page)