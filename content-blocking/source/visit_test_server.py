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
from source.setup_driver import setup_driver, get_firefox_console_logs
from source.constants import BROWSER_TYPE
from source.firewall import firewall_block_traffic, firewall_unblock_traffic
from source.test_page_server import stop_testing_server
from custom_dns_server.dns_repeater_server import DNSRepeater

TEST_SERVER_IP = "http://localhost:5000"

# tbd: client configuration where will be specified: browser type (chrome/firefox),
# browser path in case of tor/asb/brave, list of extensions to be loaded into the browser

def visit_test_server(options: dict, requests: list, dns_repeater: DNSRepeater, args, server)\
      -> list[dict]:
    """Function to simulate client visit to the test page with defined configuration"""

    # total number of all resources to check if selenium can leave the page
    total_requests = len(requests)

    def check_all_resources_loaded(driver: webdriver.Chrome | webdriver.Firefox):
        """Function to be used as a callback to check if the page has fetched all resources"""

        # Get window object with the status and check if it loaded all
        script_load_resources_status = "return window.total_fetch_count.completed == arguments[0]"
        script_load_resources_status += " && "
        script_load_resources_status += "window.total_fetch_count.pending == 0;"

        return driver.execute_script(script_load_resources_status, total_requests)

    print("Testing blocked resources for all visited pages...")

    # For debugging purposes (Avast Secure Browser doesnt work when connected through selenium)
    if args.testing_server_only:
        try:
            dns_repeater.start()
            firewall_block_traffic()
            time.sleep(3600)
        finally:
            firewall_unblock_traffic()
            dns_repeater.stop()
            stop_testing_server(server)
            exit(0)

    # Correctly setup the driver according to given config
    driver = setup_driver(options)

    # Get the console output depending on chosen browser
    browser_type = options.get(BROWSER_TYPE)

    # Wait for the extensions to load
    time.sleep(10)

    # Start DNS repeating and firewall only here, to give the browser (or extensions)
    # time to load their stuff
    if not args.early_blocking:
        dns_repeater.start()
        firewall_block_traffic()
        time.sleep(3)

    # Visit the test server
    driver.get(TEST_SERVER_IP)

    # Wait until all resources load (total_requests). Timeout in 1 hour if still waiting
    # Resources still waiting for will be considered fetched
    WebDriverWait(driver, 3600).until(check_all_resources_loaded)

    logs = None

    # Setting up for Chrome
    if browser_type == "chrome":
        logs = driver.get_log("browser")
    else:
        logs = get_firefox_console_logs(driver)

    driver.quit()

    # return console output
    return logs
