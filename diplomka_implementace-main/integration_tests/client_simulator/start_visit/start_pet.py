#
#  Copyright (C) 2019  Amit Datta
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

from .start_browser import Browser
import sys                  
import time                 
import json
import os as oslib

'''
Set up the extensions for testing. Visit the testing page.

    exp : str
        Name of the experiment.
    browsers : [str]
        Browsers to be tested this run.
    pets : [str]
        Extensions to be tested this run.
    server_config : JSON object
        Configuration of the run.
    delay : int
        Duration of page visit in seconds.
'''
def test_pet(exp, browser, pet, server_config, delay):
    try:
        def get_server_attributes(data):
            fp_sites = data["fp_sites"]
            use_socks5 = data["socks5_proxy"]
            proxy_setting = None
            if use_socks5:
                proxy_setting = data["proxy_setting"]

            return fp_sites, proxy_setting

        cwd = oslib.path.dirname(oslib.path.abspath(__file__))

        with open(oslib.path.join(cwd, "../", server_config)) as f:
            data = json.load(f)
            fp_sites, proxy_setting = get_server_attributes(data)

        unit = sim_browser(browser, pet, proxy_setting)
        
        # Here you can stop the process if all you are interested in is testing 
        # the user interactions.
        if "NBS" in pet[0] or "DLS" in pet[0]:
            sys.stdout.write("\n")
            sys.stdout.flush()
            cleanup_browser(unit)
            return

        browser = unit.get_version()
        time.sleep(5)
        html_args = "?exp="+exp+"&browser="+browser+"&pet="+'-'.join(pet)
        fp_site = fp_sites[0] + html_args
        unit.visit_sites([fp_site], delay)
        sys.stdout.write("\n")
        sys.stdout.flush()

        cleanup_browser(unit)
    except Exception as e:
        print(e)

'''
Create a browser instance.
    browser : str
        Browser definition - Chrome or Firefox and a version.
    pet : [str]
        List of extensions to install.
    proxy_settings : str
        Optional proxy settings to set the browser up with.

    ------------------------------------------------------------

    b : object
        Browser object instance.
'''
def sim_browser(browser, pet, proxy_setting):
    b = Browser(browser, pet, proxy_setting)
    return b

def check(unit, fp_list):
    unit.visit_sites(fp_list)

def cleanup_browser(unit):
    unit.quit()

if __name__ == '__main__':
    EXP = sys.argv[1]
    BROWSER = sys.argv[2]
    PET = sys.argv[3]
    SERVER_CONFIG = sys.argv[4] 

    test_pet(EXP, BROWSER, PET, SERVER_CONFIG)
