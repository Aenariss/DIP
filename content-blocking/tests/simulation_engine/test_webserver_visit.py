# test_webserver_visit.py
# Test the functions used in visit_test_server.py from simulation_engine
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

# Custom modules
from source.simulation_engine.visit_test_server import visit_test_server
from source.simulation_engine.visit_test_server import check_all_resources_loaded

class TestWebServerVisit(unittest.TestCase):

    @patch("source.simulation_engine.visit_test_server.setup_driver")
    @patch("source.simulation_engine.visit_test_server.firewall_block_traffic")
    @patch("source.simulation_engine.visit_test_server.DNSRepeater")
    @patch("source.simulation_engine.visit_test_server.get_firefox_console_logs")
    @patch("source.simulation_engine.visit_test_server.webdriver.Chrome")
    @patch("source.simulation_engine.visit_test_server.webdriver.Firefox")
    @patch("source.simulation_engine.visit_test_server.WebDriverWait")
    @patch("time.sleep", return_value=None)
    def test_visit_test_server(self, mock_sleep, mock_webdriver_wait, mock_firefox, mock_chrome,\
                    mock_get_firefox_logs, mock_dns_repeater, mock_firewall, mock_setup_driver):
        """Test visit_test_server function with Chrome and Firefox"""

        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        mock_webdriver_wait.return_value.until.return_value = True

        # Mock logs returned from browser console
        mock_chrome_log = [{"message": "chrome"}]
        mock_firefox_log = [{"message": "firefox"}]
        mock_driver.get_log.return_value = mock_chrome_log
        mock_get_firefox_logs.return_value = mock_firefox_log

        test_requests = ["https://a.com/", "https://b.com/"]
        test_dns_repeater = MagicMock()
        test_args = MagicMock(early_blocking=False)

        class Config_chrome:
            browser_type = "chrome"
            browser_initialization_time = 0.1

        class Config_firefox:
            browser_type = "firefox"
            browser_initialization_time = 0.1

        chrome_instance_config = Config_chrome()
        firefox_instance_config = Config_firefox()

        # Test with Chrome
        logs = visit_test_server(chrome_instance_config, test_requests, test_dns_repeater,\
                                test_args)
        self.assertEqual(logs, mock_chrome_log)

        mock_setup_driver.assert_called_with(chrome_instance_config)

        # Test with Firefox
        logs = visit_test_server(firefox_instance_config, test_requests, test_dns_repeater,\
                                test_args)
        self.assertEqual(logs, mock_firefox_log)

        mock_setup_driver.assert_called_with(firefox_instance_config)

        self.assertEqual(test_dns_repeater.start.call_count, 2)
        self.assertEqual(mock_firewall.call_count, 2)
        mock_driver.get.assert_called_with("http://localhost:5000")
        self.assertEqual(mock_driver.get.call_count, 2)
        self.assertEqual(mock_driver.quit.call_count, 2)

    def test_check_all_resources_loaded_success(self):
        """Test when all resources are successfully loaded"""
        mock_driver = MagicMock()
        mock_driver.execute_script.return_value = True

        script = "return window.total_fetch_count.completed"
        script += " == "
        script += "arguments[0] && window.total_fetch_count.pending == 0;"

        result = check_all_resources_loaded(mock_driver, 5)
        self.assertTrue(result)
        mock_driver.execute_script.assert_called_once_with(script, 5)

    def test_check_all_resources_loaded_pending(self):
        """Test when not all resources are already loaded"""
        mock_driver = MagicMock()
        mock_driver.execute_script.return_value = False

        result = check_all_resources_loaded(mock_driver, 5)
        self.assertFalse(result)
