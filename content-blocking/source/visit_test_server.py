# visit_test_server.py
# Definition of function to visit test server and log results
# Copyright (C) 2025 Vojtěch Fiala
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.
#

# Built-in modules
import time

# 3rd-party modules
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

# Custom modules
from source.setup_driver import setup_driver

TEST_SERVER_IP = "http://localhost:5000"

# tbd: client configuration where will be specified: browser type (chrome/firefox),
# browser path in case of tor/asb/brave, list of extensions to be loaded into the browser

def visit_test_server(original_page: str, client_config: dict, requests: list) -> list[dict]:
    """Function to simulate client visit to the test page with defined configuration"""

    # total number of all resources to check if selenium can leave the page
    total_requests = len(requests)

    def check_all_resources_loaded(driver: webdriver):
        """Function to be used as a callback to check if the page has fetched all resources"""

        # Get window object with the status and check if it loaded all
        script_load_resources_status = "return window.total_fetch_count.completed == arguments[0]"
        script_load_resources_status += " && "
        script_load_resources_status += "window.total_fetch_count.pending == 0;"

        return driver.execute_script(script_load_resources_status, total_requests)

    print("Testing blocked resources for", original_page)

    # Correctly setup the driver according to given config
    driver = setup_driver(client_config)

    # Wait for the extensions to load
    time.sleep(10)

    # Visit the test server
    driver.get(TEST_SERVER_IP)

    # Wait until all resources load (total_requests). Timeout in 60 sec if still waiting
    # Resources still waiting for will be considered fetched
    WebDriverWait(driver, 30).until(check_all_resources_loaded)

    # Get the console output
    logs = driver.get_log("browser")

    driver.quit()

    # return console output
    return logs
