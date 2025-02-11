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

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver(config: dict) -> webdriver:

    extension_path = "./addons/ad_block_plus_4_12_0.crx"
    
    # Set up Chrome options and enable DevTools Protocol
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("auto-open-devtools-for-tabs")
    chrome_options.add_argument("--enable-javascript")

    chrome_options.add_extension(extension_path)

    chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver