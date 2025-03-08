# setup_driver.py
# Functions to correctly set-up selenium driver with defined browser and extensions
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

# 3rd-party modules
from selenium import webdriver
import selenium.webdriver.chrome.service as ChromeService
import selenium.webdriver.chrome.options as ChromeOptions
import selenium.webdriver.firefox.options as FirefoxOptions
import selenium.webdriver.firefox.service as FirefoxService

# Custom modules
from source.constants import BROWSER_TYPE, BROWSER_VERSION, USING_CUSTOM_BROWSER, TESTED_ADDONS
from source.constants import CHROME_ADDONS_FOLDER, FIREFOX_ADDONS_FOLDER, GENERAL_ERROR
from source.constants import TIME_UNTIL_TIMEOUT, LOGGING_BROWSER_VERSION, JSHELTER_FPD_PATH
from source.constants import CUSTOM_BROWSER_BINARY, FIREFOX_RESOURCE_LOGGER

def setup_driver(options: dict) -> webdriver.Chrome | webdriver.Firefox:
    """Function to setup the driver depeneding on the specified browser"""
    browser_type = options.get(BROWSER_TYPE)
    # Setting up for Chrome
    if browser_type == "chrome":
        return setup_chrome(options)

    # If chrome wasnt selected, lets suppose it was firefox
    return setup_firefox(options)

def setup_chrome(options: dict) -> webdriver.Chrome:
    """Function to setup driver for chrome-based browser"""

    # Check if we're using custom browser
    if options.get(USING_CUSTOM_BROWSER):

        custom_browser_path = options.get(CUSTOM_BROWSER_BINARY)

        chrome_options = ChromeOptions.Options()
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--enable-javascript")

        # use custom binary
        chrome_options.binary_location = custom_browser_path

        # Go through all specified extensions and add them
        # Will not be used in the thesis, but allows more potential flexibility
        try:
            for extension in options.get(TESTED_ADDONS):
                chrome_options.add_extension(CHROME_ADDONS_FOLDER + extension)
        except Exception:
            print(f"Error loading extension {extension}. Is it present in {CHROME_ADDONS_FOLDER}?")
            exit(GENERAL_ERROR)

        chromedriver_path = "./chromedriver_132.exe"
        service = ChromeService.Service(chromedriver_path)

        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver
    else:
        chrome_options = ChromeOptions.Options()
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--enable-javascript")
        chrome_options.browser_version = options.get(BROWSER_VERSION)

        # Go through all specified extensions and add them
        try:
            for extension in options.get(TESTED_ADDONS):
                chrome_options.add_extension(CHROME_ADDONS_FOLDER + extension)
        except Exception:
            print(f"Error loading extension {extension}. Is it present in {CHROME_ADDONS_FOLDER}?")
            exit(GENERAL_ERROR)

        # Set logging capabilities
        chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

        service = ChromeService.Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

def get_firefox_console_logs(driver):
    """Function to get logs from Firefox console"""

    # Get performance entries
    resource_logs = driver.execute_script("""
        var logs = observedResources;
        return JSON.stringify(logs);
    """)

    return json.loads(resource_logs)

def setup_firefox(options: dict) -> webdriver.Firefox:
    """Function to setup driver for firefox-based browser"""

    # Check if we're using custom browser
    if options.get(USING_CUSTOM_BROWSER):
        # tbd
        return None
    else:
        firefox_options = FirefoxOptions.Options()

        # Turn off Firefox Extended Protection and DNS-over-HTTPS
        firefox_options.set_preference("privacy.trackingprotection.custom.enabled", False)
        firefox_options.set_preference("privacy.trackingprotection.enabled", False)
        firefox_options.set_preference("privacy.trackingprotection.pbmode.enabled", False)
        firefox_options.set_preference("privacy.trackingprotection.socialtracking.enabled", False)
        firefox_options.set_preference("privacy.trackingprotection.cryptomining.enabled", False)
        firefox_options.set_preference("privacy.trackingprotection.fingerprinting.enabled", False)
        firefox_options.set_preference("network.trr.mode", 5)

        service = FirefoxService.Service()
        driver = webdriver.Firefox(options=firefox_options, service=service)

        # Install the logging extension
        driver.install_addon(FIREFOX_RESOURCE_LOGGER, temporary=True)

        # Go through all specified extensions and add them
        try:
            for extension in options.get(TESTED_ADDONS):
                driver.install_addon(FIREFOX_ADDONS_FOLDER + extension, temporary=True)
        except Exception:
            print(f"Error loading extension {extension}. Is it present in {FIREFOX_ADDONS_FOLDER}?")
            exit(GENERAL_ERROR)

        return driver

def setup_jshelter_custom_fpd(options: dict, download_path: str) -> webdriver.Chrome:

    # Set up Chrome options and enable DevTools Protocol
    chrome_options = ChromeOptions.Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument('--enable-extensions')
    # I already collected traffic without this setting, maybe enable in the future?
    #chrome_options.add_argument('--ignore-certificate-errors')
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

    service = ChromeService.Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Wait at most this time (seconds) for a page to load
    driver.set_page_load_timeout(options.get(TIME_UNTIL_TIMEOUT))

    return driver
