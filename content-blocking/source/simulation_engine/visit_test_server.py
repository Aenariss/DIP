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
from config import Config
from source.setup_driver import setup_driver, get_firefox_console_logs
from source.simulation_engine.firewall import firewall_block_traffic
from source.simulation_engine.custom_dns_server.dns_repeater_server import DNSRepeater

TEST_SERVER_IP = "http://localhost:5000"

def check_all_resources_loaded(driver: webdriver.Chrome | webdriver.Firefox, total_requests: int):
    """Function to be used as a callback to check if the page has fetched all resources
    
    Args:
        driver: An instance of a webdriver which opened the test page
        total_requests: Number of requests fetched on the testing page
    """

    # Get window object with the status and check if it loaded all
    script_load_resources_status = "return window.total_fetch_count.completed == arguments[0]"
    script_load_resources_status += " && "
    script_load_resources_status += "window.total_fetch_count.pending == 0;"

    return driver.execute_script(script_load_resources_status, total_requests)

def visit_test_server(options: Config, requests: list, dns_repeater: DNSRepeater, args)\
      -> list[dict]:
    """Function to simulate client visit to the test page with defined configuration
    
    Args:
        options: Valid instance of Config
        requests: list of all requests in the request trees, 
        the same which was used to initialize server
        dns_repeater: Instance of DNSRepeater which repeats DNS responses
        args: Arguments inputted by the client

    Returns:
        list[dict]: Simulation output, format depends on chosen browser
    """

    # total number of all resources to check if selenium can leave the page
    total_requests = len(requests)

    print("Testing blocked resources for all visited pages...")

    # Correctly setup the driver according to given config
    driver = setup_driver(options)

    # Get the console output depending on chosen browser
    browser_type = options.browser_type

    # Wait for the extensions to load
    time.sleep(options.browser_initialization_time)

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
    WebDriverWait(driver, 3600).until(lambda driver:\
                                check_all_resources_loaded(driver, total_requests))

    logs = None

    # Setting up for Chrome
    if browser_type == "chrome":
        logs = driver.get_log("browser")
    else:
        logs = get_firefox_console_logs(driver)

    driver.quit()

    # return console output
    return logs
