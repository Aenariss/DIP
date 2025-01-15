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

import pytest
import re
import os
import datetime
from store_values import create_browser_data
from shared_set import set_shared_noaddon, set_shared_addonRun, set_shared_level, set_shared_browser, set_shared_addonsInstalled

def sort_extensions(addonsTested):
    extensions = addonsTested.split("-")
    sorted_extensions = sorted(extensions)
    sorted_addonsTested = '_'.join(sorted_extensions)
    extensions_listing = ', '.join(sorted_extensions)
    return sorted_addonsTested, extensions_listing

## Main module - it starts and control testing.
#
#  To start testing call this module from PowerShell, CommandPrompt, Terminal or Bash: python start.py
#  Currently only the data inside a subfolder with todays date is tested. 
def main():

    generated_t = str(datetime.datetime.now(datetime.timezone.utc))
    test_start = generated_t.replace(" ", "--").replace(":", "-").replace(".", "-")
    test_date = r"\d{4}-\d{2}-\d{2}"
    test_date_timestamp = re.search(test_date, test_start).group(0)

    subfolders = [f for f in os.listdir("/usr/app/src/fingerprinting_server/outputs/" + test_date_timestamp) if os.path.isdir(os.path.join("/usr/app/src/fingerprinting_server/outputs/" + test_date_timestamp, f))]
    print("Integration testing starting.")
    for subfolder in subfolders:
        browser_name = subfolder.split('_')[-1]
        browser_data = create_browser_data(test_date_timestamp + "/" + subfolder)  

        if not browser_data:
            print("Integration testing skipped, no data found")
            exit(0)

        print("Testing log files in directory: ", test_date_timestamp + "/" + subfolder)
        print("Browser currently tested:", browser_name)

        if "special" in browser_name:
            browser_name = "special"
        else:
            browser_name = browser_name.split("=")[0]
    
        no_addon = browser_data[0]
        set_shared_browser(browser_name)
        set_shared_noaddon(no_addon)


        for value in browser_data[1:]:     
                sorted_addonsTested, soretd_names = sort_extensions(value.addons)      
                set_shared_addonsInstalled(sorted_addonsTested)           
                if "JS" in sorted_addonsTested:
                    js_level = re.search(r'\d+', sorted_addonsTested).group(0)
                    print("JShelter level tested:", js_level)
                    set_shared_level(js_level)
                else:
                    set_shared_level(0)               
                set_shared_addonRun(value)     
                print("Addons installed this run: ", soretd_names)
                      
                pytest.main(['-s'])       
        print("\n")           

if __name__ == "__main__":
    main()
    print("Integration testing ended.")
