# network_logs_loader.py
# Observe network traffic on a given page and return it as a dictionary.
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Custom modules
from source.constants import TRAFFIC_FOLDER
from source.setup_driver import setup_chrome_for_traffic_logging
from source.config import Config

def enable_developer_mode(driver: webdriver.Chrome) -> None:
    """Function to enable developer mode inside Selenium-driven Chrome

        Args:
            driver: The Selenium driver for Chrome
    """

    # Open page with extension settings
    driver.get("chrome://extensions")

    # Everything is inside <extensions-manager></>, wait for it to load
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.TAG_NAME, "extensions-manager")
    ))

    # Everything is inside shadow root inside <extensions-amanger>
    shadow_root = driver.find_element(By.TAG_NAME, "extensions-manager").shadow_root

    # Get toolbar inside shadow root
    toolbar = shadow_root.find_element(By.ID, "toolbar")

    # The button is in <cr-toggle id="devMode"> inside toolbar shadowroot
    toolbar_shadow = toolbar.shadow_root
    dev_mode_button = toolbar_shadow.find_element(By.ID, "devMode")

    # Click the button to enable devmode
    dev_mode_button.click()

    # Now click update to apply the devmode
    # Update button is inside toolbar shadow as <cr-button id="updateNow">
    update_button = toolbar_shadow.find_element(By.ID, "updateNow")

    # Click using JavaScript since normal .click() doesnt work
    driver.execute_script("arguments[0].click();", update_button)

    time.sleep(0.5)

def is_internal_network_event(log: dict) -> bool:
    """Function to be used during network requests parsing.
    Decides whether a given network log is an internal request.

    Args:
        log: A dict of Network.requestWillBeSent event
        
    Returns:
        status (bool): Whether the provided event corresponds to an internal request
    """
    status = False

    # Skip internal devtools requests
    if "devtools://" in log["params"]["request"]["url"] or\
        "devtools://" in log["params"]["documentURL"]:
        status = True

    # Skip chrome internal pages
    if "chrome://" in log["params"]["request"]["url"] or\
        "chrome://" in log["params"]["documentURL"]:
        status = True

    # Skip JShelter loaded data
    if "https://[ff00::]/chrome-extension://" in log["params"]["request"]["url"] or\
        "https://[ff00::]/chrome-extension://" in log["params"]["documentURL"]:
        status = True

    return status

def last_valid_parent(stack: dict) -> dict:
    """Function to be recursively called to find first non-empty parent url in
    callstack to decrease log size

    Args:
        stack: Dictionary containing the initiator.stack

    Returns:
        dict: New stack containing only one final caller or empty stack if none available
            
    """
    call_frames = stack.get("callFrames", [])
    for call in call_frames:

        # Skip empty strings JShelter overrides
        if call["url"] != "" and not call["url"].startswith("chrome"):

            # Keep the original structure
            return {"stack": {"callFrames": [call]}}

    # Check parent stack exists before delving deeper
    if stack.get("parent"):

        # No valid find (or callFrame empty), go deeper
        return last_valid_parent(stack["parent"])

    # No parent, didn't find anything, return blank parent
    empty_stack = {"stack": {"callFrames": []}}
    return empty_stack

def reduce_initiator_callstack(log: dict) -> dict:
    """Function to be used when 'compact' flag was set to reduce size of saved logs
    
        Args:
            log: A dict of Network.requestWillBeSent event
        
        Returns:
            reduced_initiator: Initiator field containing only the final valid caller
    """
    tmp_initiator = log["params"]["initiator"]
    reduced_log = {}

    # Only compactize if stack is present
    if tmp_initiator.get("stack"):

        # Recursively go until you find the first non-empty non-JShelter
        # parent and save only them
        reduced_log = last_valid_parent(tmp_initiator["stack"])
        reduced_log["type"] = tmp_initiator["type"]
    else:
        reduced_log = log["params"]["initiator"]

    return reduced_log

def log_event_attributes(log: dict, compact: bool) -> dict:
    """Function to create a dict containing only the important
    attributes of the network event log
    
    Args:
        log: A dict of Network.requestWillBeSent event
        compact: Whether to save only the final caller in the initiator call stack to reduce
                size of saved logs
        
    Returns:
        reduced_log (dict): A log containing only the important attributes for evaluation
    """
    reduced_log = {}

    # Used only for checks
    reduced_log["requested_for"] = log["params"]["documentURL"]

    # Used to establish which request was sent first to later match DNS responses
    reduced_log["time"] = log["params"]["timestamp"]

    # Just useless stuff, but log it anyway cause it might be useful maybe later
    reduced_log["requestId"] = log["params"]["requestId"]
    reduced_log["loaderId"] = log["params"]["loaderId"]

    # "Name" of the reosurce in the F12 Network traffic
    reduced_log["requested_resource"] = log["params"]["request"]["url"]

    # If compact is set, only save till the final valid caller in the call stack
    if compact:
        reduced_log["initiator"] = reduce_initiator_callstack(log)
    else:
        reduced_log["initiator"] = log["params"]["initiator"]

    return reduced_log

def get_network_requests(logs: dict, compact: bool) -> list[dict]:
    """Function to extract the desired attributes from Network.requestWillBeSent events
    
        Args:
            logs: Chromium performance logs ("goog:loggingPrefs", {"performance": "ALL"})
            compact: Whether to save only the final caller in the initiator call stack to reduce
                size of saved logs

        Returns:
            parsed_logs (list[dict]): List containing all network.RequestWillBeSent events with
                the required attributes
    """
    parsed_logs = []
    # Go through all the recorded logs
    for log in logs:
        log = json.loads(log["message"])["message"]

        # Filter in only the logs with required data
        if log["method"] == "Network.requestWillBeSent":

            # Skip internal requests
            if is_internal_network_event(log):
                continue

            new_log_with_values = log_event_attributes(log, compact)
            parsed_logs.append(new_log_with_values)

    return parsed_logs

def get_page_network_traffic(page: str, options: Config, compact: bool) -> list:
    """Function to load page network traffic.

        Args:
            page: String with the page URL
            options: Instance of Config
            compact: Whether to compactize 

        Returns:
            network_logs (list): List of observed Network.requestWillBeSent events
    """

    print("Visiting page", page)

    # Download folder needs to be an absolute path
    download_path = os.path.abspath(TRAFFIC_FOLDER)
    driver = setup_chrome_for_traffic_logging(options, download_path)

    # Sleep to allow JShelter to load
    time.sleep(2)

    # Enable developer mode so that FP can function
    enable_developer_mode(driver)

    # Visit the specified page and spend some time there
    try:
        driver.get(page)

        # Wait at the page for a user-specified time
        page_wait_time = options.page_wait_time
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
