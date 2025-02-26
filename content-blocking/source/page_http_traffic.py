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
import os
import time

# 3rd-party modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pyautogui

# Custom modules
from source.constants import PAGE_WAIT_TIME, TRAFFIC_FOLDER, JSHELTER_FPD_PATH
from source.constants import LOGGING_BROWSER_VERSION

def get_page_traffic(page: str, options: dict, compact: bool) -> list:
    """Function to load page network traffic. Returns observed network traffic and 
       saves FPD report into traffic folder"""

    print("Visiting page", page)

    download_path = os.path.abspath(TRAFFIC_FOLDER)

    # Set up Chrome options and enable DevTools Protocol
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument('--enable-extensions')
    chrome_options.browser_version = options.get(LOGGING_BROWSER_VERSION)
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True
    })

    # Set-up JShelter FPD -- custom version, all shields are off, fpd is set on by default
    chrome_options.add_extension(JSHELTER_FPD_PATH)

    # Allow logging of network traffic
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Wait at most this time (seconds) for a page to load
    driver.set_page_load_timeout(10)

    # Enable developer mode so that FP can function
    enable_developer_mode(driver)

    # Visit the specified page and spend some time there
    try:
        driver.get(page)

        # Wait at the page for a user-specified time
        page_wait_time = options.get(PAGE_WAIT_TIME)
        time.sleep(page_wait_time)

        # Get network logs
        network_logs = driver.get_log('performance')
    except Exception:
        return {}
    finally:
        driver.quit()

    # Parse the logs
    network_logs = get_network_requests(network_logs, compact)

    return network_logs

def enable_developer_mode(driver) -> None:
    """Function to enable developer mode inside Selenium"""
    driver.get("chrome://extensions")

    time.sleep(0.5)

    pyautogui.click(1250, 225)

    time.sleep(0.5)

    pyautogui.click(370, 275)

    time.sleep(0.5)

def get_network_requests(logs: dict, compact: bool) -> list[dict]:
    """Function to extract only the initiator chain from the observed data"""
    parsed_logs = []
    # Go through all the recorded logs
    for log in logs:
        log = json.loads(log["message"])["message"]

        # Filter in only the logs with required data
        if log["method"] == "Network.requestWillBeSent":
            # Skip internal devtools requests
            if "devtools://" in log["params"]["request"]["url"] or\
               "devtools://" in log["params"]["documentURL"]:
                continue

            # Skip chrome internal pages
            if "chrome://" in log["params"]["request"]["url"] or\
               "chrome://" in log["params"]["documentURL"]:
                continue
            tmp_log = {}

            # Unimportant for evaluation? used only for checks
            tmp_log["requested_by"] = log["params"]["documentURL"]

            # Used to establish which request was sent first to later match DNS responses
            tmp_log["time"] = log["params"]["timestamp"]


            # "Name" of the reosurce in the F12 Network traffic
            tmp_log["requested_resource"] = log["params"]["request"]["url"]

            # Initiator chain
            # tbd: If something was called dynamically (in browser shows as VM:xxx)
            # it shows as blank url, improve?
            # If compact is set, only save till the first valid initiator
            if compact:
                tmp_initiator = log["params"]["initiator"]

                # Only compact-ize if stack is present
                if tmp_initiator.get("stack"):

                    # Recursively go until you find the first non-empty non-JShelter
                    # parent and save only them
                    tmp_log["initiator"] = first_valid_parent(tmp_initiator["stack"])
                    tmp_log["initiator"]["type"] = tmp_initiator["type"]
                else:
                    tmp_log["initiator"] = log["params"]["initiator"]
            else:
                tmp_log["initiator"] = log["params"]["initiator"]
            parsed_logs.append(tmp_log)

    return parsed_logs

def first_valid_parent(stack: dict) -> dict:
    """Function to be recursively called to find first non-empty parent url in callstack"""
    call_frames = stack.get("callFrames", [])
    for call in call_frames:

        # Skip empty strings JShelter overrides
        if call["url"] != "" and not call["url"].startswith("chrome"):

            # Keep the original structure
            return {"stack": {"callFrames": [call]}}

    # Check parent stack exists before delving deeper
    if stack.get("parent"):

        # No valid find (or callFrame empty), go deeper
        return first_valid_parent(stack["parent"])

    # No parent, didn't find anything, return blank parent
    empty_stack = {"stack": {"callFrames": []}}
    return empty_stack
