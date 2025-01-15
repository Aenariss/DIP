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

import random 
import time
from selenium.webdriver.support.select import Select

domains = ["www.fsf.org", "gnu.org", "jshelter.org", "www.fit.vutbr.cz"]
levels = ['0', '2', '3', 'Experiment']

def set_domain_level(driver, options_page, domain, level):
    driver.get(options_page.replace("/options.html", "/options_domains.html"))
    time.sleep(0.5)
    driver.find_elements('id', 'domain-text')[0].send_keys(domain)
    select = Select(driver.find_elements('id', 'domain-level')[0])
    select.select_by_value(level)
    driver.find_elements('id', 'add_domain')[0].click()

	
def unset_domain_level(driver, options_page, domain):
    driver.get(options_page.replace("/options.html", "/options_domains.html"))
    time.sleep(0.5)
    driver.find_elements('id', 'delete-dl-' + domain)[0].click()
 
	
def change_domain_level(driver, options_page, domain, level):
    driver.get(options_page.replace("/options.html", "/options_domains.html"))
    time.sleep(0.5)
    select = Select(driver.find_elements('id', 'dl-change-' + domain)[0])
    select.select_by_value(level)
    driver.find_elements('id', 'overwrite-dl-' + domain)[0].click()

	
def get_domain_level(driver, options_page, domain):
    driver.get(options_page.replace("/options.html", "/options_domains.html"))
    time.sleep(0.5)
    select = Select(driver.find_elements('id', 'dl-change-' + domain)[0])
    selected_option = select.first_selected_option
    return selected_option.get_attribute("value")

	
## Test setting a level for the selected domains.	
def test_setting_domain_level(driver, options_page):
    for i in range(len(domains)):
        domain = domains[i]
        level = random.choice(levels)
        set_domain_level(driver, options_page, domain, level)
        if get_domain_level(driver, options_page, domain) == level:
            print("Domain level set correctly, test has passed.")
        else:
            print("Failed to set the correct domain level.")

	
## Test changing a level for the selected domains.	
def test_change_domain_level(driver, options_page):
    for i in range(len(domains)):
        domain = domains[i]
        level = random.choice(levels)
        change_domain_level(driver, options_page, domain, level)
        if get_domain_level(driver, options_page, domain) == level:
            print("Domain level set correctly, test has passed.")
        else:
            print("Failed to set the correct domain level.")
        
        # Tear down.
        unset_domain_level(driver, options_page, domain)