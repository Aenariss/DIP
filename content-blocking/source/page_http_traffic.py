# page_http_traffic.py
# Observe HTTP traffic on a given page and return it as a dictionary.
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
import json
import time

# 3rd-party modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Custom modules
from source.constants import PAGE_WAIT_TIME

def get_page_traffic(page: str, options: dict) -> dict:
    """Function to load page network traffic"""

    print("Visiting page", page)

    # Set up Chrome options and enable DevTools Protocol
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("auto-open-devtools-for-tabs")
    chrome_options.add_argument("--enable-javascript")

    # Allow logging
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Visit the specified page
    driver.get(page)

    # Wait at the page for a user-specified time
    page_wait_time = options.get(PAGE_WAIT_TIME)
    time.sleep(page_wait_time)

    # Get network logs
    network_logs = driver.get_log('performance')

    driver.quit()

    # Parse the logs
    network_logs = get_network_requests(network_logs)

    return network_logs

def get_network_requests(logs: dict) -> dict:
    """Function to extract only the initiator chain from the observed data"""
    parsed_logs = []
    # Go through all the recorded logs
    for log in logs:
        log = json.loads(log["message"])["message"]

        # Filter in only the logs with required data
        if "Network.requestWillBeSent" == log["method"]:
            # Skip internal devtools requests
            if "devtools://" in log["params"]["request"]["url"]:
                continue
            tmp_log = {}

            # Unimportant for evaluation? used only for checks
            tmp_log["requested_by"] = log["params"]["documentURL"]

            # "Name" of the reosurce in the F12 Network traffic
            tmp_log["requested_resource"] = log["params"]["request"]["url"]

            # Initiator chain
            # tbd: If something was called dynamically (in browser shows as VM:xxx)
            # it shows as blank url, improve?
            tmp_log["initiator"] = log["params"]["initiator"]
            parsed_logs.append(tmp_log)

    return parsed_logs
