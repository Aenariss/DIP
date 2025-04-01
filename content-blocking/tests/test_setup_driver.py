# test_setup_driver.py
# Test driver is set up correctly
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
import unittest
from unittest.mock import patch, MagicMock
import json

# Custom modules
from source.config import Config
from source.setup_driver import setup_chrome, setup_chrome_for_traffic_logging
from source.setup_driver import setup_firefox, get_firefox_console_logs, setup_driver

class TestSetupDriver(unittest.TestCase):

    @patch('source.setup_driver.webdriver.Chrome')
    @patch('source.setup_driver.webdriver.Firefox')
    def test_setup_driver_chrome(self, mock_firefox, mock_chrome):
        """Test driver can be set up correctly for chrome"""
        class ConfigChrome:
            browser_type = "chrome"
            using_custom_browser = False
            chrome_browser_version = "134"
            tested_addons = []

        mock_chrome_instance = MagicMock()
        mock_chrome.return_value = mock_chrome_instance

        driver = setup_driver(ConfigChrome())
        self.assertEqual(driver, mock_chrome_instance)
        mock_chrome.assert_called_once()
        mock_firefox.assert_not_called()

    @patch('source.setup_driver.webdriver.Chrome')
    def test_setup_driver_chrome_custom(self, mock_chrome):
        """Test driver can be set up correctly for custom chrome-browser"""
        class ConfigChrome:
            browser_type = "chrome"
            using_custom_browser = True
            chrome_browser_version = "134"
            tested_addons = []
            custom_browser_binary = "./path.exe"
            profile = "./profile"
            chromedriver_path = "./chromedriver"
            experiment_name = "avast_browser"

        mock_chrome_instance = MagicMock()
        mock_chrome.return_value = mock_chrome_instance

        driver = setup_driver(ConfigChrome())
        self.assertEqual(driver, mock_chrome_instance)
        mock_chrome.assert_called_once()

    @patch('source.setup_driver.webdriver.Chrome')
    @patch('source.setup_driver.webdriver.chrome.options.Options')
    def test_setup_driver_chrome_custom_exception(self, mock_options, mock_chrome):
        """Test driver can be set up correctly for custom chrome-browser"""
        class ConfigChrome:
            browser_type = "chrome"
            using_custom_browser = True
            chrome_browser_version = "134"
            tested_addons = ["ext"]
            custom_browser_binary = "./path.exe"
            profile = "./profile"
            chromedriver_path = "./chromedriver"
            experiment_name = "avast_browser"

        mock_options_instance = mock_options.return_value
        mock_options_instance.add_extension.side_effect = Exception()

        # Check it correctly gives an error
        with self.assertRaises(SystemExit):
            driver = setup_driver(ConfigChrome())

    @patch('source.setup_driver.webdriver.Chrome')
    @patch('source.setup_driver.webdriver.chrome.options.Options')
    def test_setup_driver_chrome_exception(self, mock_options, mock_chrome):
        """Test driver can be set up correctly for custom chrome-browser"""
        class ConfigChrome:
            browser_type = "chrome"
            using_custom_browser = False
            chrome_browser_version = "134"
            tested_addons = ["ext"]
            custom_browser_binary = "./path.exe"
            profile = "./profile"
            chromedriver_path = "./chromedriver"
            experiment_name = "avast_browser"

        mock_options_instance = mock_options.return_value
        mock_options_instance.add_extension.side_effect = Exception()

        # Check it correctly gives an error
        with self.assertRaises(SystemExit):
            driver = setup_driver(ConfigChrome())

    @patch('source.setup_driver.webdriver.Chrome')
    @patch('source.setup_driver.webdriver.Firefox')
    def test_setup_driver_firefox(self, mock_firefox, mock_chrome):
        """Test driver can be set up correctly for FF"""
        class ConfigFirefox:
            browser_type = "firefox"
            using_custom_browser = False
            use_firefox_default_protection = False
            tested_addons = []

        mock_firefox_instance = MagicMock()
        mock_firefox.return_value = mock_firefox_instance

        driver = setup_driver(ConfigFirefox())
        self.assertEqual(driver, mock_firefox_instance)
        mock_firefox.assert_called_once()
        mock_chrome.assert_not_called()

    @patch('source.setup_driver.webdriver.Firefox')
    def test_setup_driver_firefox_exception(self, mock_firefox):
        """Test driver can be set up correctly for FF"""
        class ConfigFirefox:
            browser_type = "firefox"
            using_custom_browser = False
            use_firefox_default_protection = True
            tested_addons = ["addon"]

        mock_firefox_instance = MagicMock()
        mock_firefox.return_value = mock_firefox_instance
        mock_firefox_instance.install_addon.side_effect = [True, Exception()]

        # Check it correctly gives an error
        with self.assertRaises(SystemExit):
            driver = setup_driver(ConfigFirefox())

    def test_setup_driver_firefox_custom_error(self):
        """Test driver can be set up correctly for FF"""
        class ConfigFirefox:
            browser_type = "firefox"
            using_custom_browser = True
            use_firefox_default_protection = False
            tested_addons = []

        driver = setup_driver(ConfigFirefox())
        self.assertEqual(driver, None)

    @patch("selenium.webdriver.Firefox")
    def test_get_firefox_console_logs(self, mock_firefox):
        """Test FF logs are obtained correctly"""
        driver = mock_firefox()
        driver.execute_script.return_value = json.dumps(["http://test.com"])

        logs = get_firefox_console_logs(driver)
        self.assertEqual(logs, ["http://test.com"])
        driver.execute_script.assert_called_once()

    @patch("selenium.webdriver.Chrome")
    @patch("selenium.webdriver.chrome.service.Service")
    def test_setup_chrome_for_traffic_logging(self, mock_chrome_service, mock_chrome):
        """Test logging chromedriver is being returned"""
        class ConfigChrome:
            browser_type = "chrome"
            using_custom_browser = False
            chrome_browser_version = "134"
            tested_addons = ["ext"]
            custom_browser_binary = "./path.exe"
            profile = "./profile"
            chromedriver_path = "./chromedriver"
            experiment_name = "avast_browser"
            headless_logging = True
            logging_browser_version = "134"
            time_until_timeout = 30

        download_path = "/fake/path"
        mock_driver = mock_chrome.return_value

        driver = setup_chrome_for_traffic_logging(ConfigChrome(), download_path)
        self.assertEqual(driver, mock_driver)
        mock_chrome.assert_called_once()
