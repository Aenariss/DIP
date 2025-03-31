# test_network_logs_loader.py
# Test the functions used in network logs loader from traffic_logger
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
from unittest.mock import MagicMock, patch

# Custom modules
from source.traffic_logger.network_logs_loader import is_internal_network_event, last_valid_parent
from source.traffic_logger.network_logs_loader import reduce_initiator_callstack
from source.traffic_logger.network_logs_loader import get_network_requests, get_page_network_traffic
from source.traffic_logger.network_logs_loader import enable_developer_mode

class TestNetworkLogsLoader(unittest.TestCase):

    def test_is_internal_network_event(self):
        """Test that internal network events are correctly flagged"""
        log = {"params": {"request": {"url": "chrome://extensions"}, "documentURL": ""}}
        self.assertTrue(is_internal_network_event(log))

        log = {"params": {"request": {"url": "https://[ff00::]/chrome-extension://test"},\
                        "documentURL": ""}}
        self.assertTrue(is_internal_network_event(log))

        log = {"params": {"request": {"url": "devtools://something"}, "documentURL": ""}}
        self.assertTrue(is_internal_network_event(log))

        log = {"params": {"request": {"url": "https://vut.cz"}, "documentURL":\
                        "https://fit.vut.cz"}}
        self.assertFalse(is_internal_network_event(log))

    def test_last_valid_parent(self):
        """Test that last valid parent is correctly obtained"""
        # Stack can have parents, in that case I want the last caller that is valid
        stack = {
            "callFrames": [{"url": "chrome://something"}, 
                           {"url": "https://valid.example.com/a.js"}],
            "parent": {"callFrames": [{"url": "https://valid.parent.com/b.js"}]}
        }

        # Check result is the first valid URL of the stack
        result = last_valid_parent(stack)
        self.assertEqual(result["stack"]["callFrames"][0]["url"], "https://valid.example.com/a.js")

        stack = {"callFrames": [
                    {"url": ""},
                    {"url": "https://static.xx.fbcdn.net/rsrc.php/v4/y0/r/zzXQOjhbNNC.js"},
                    {"url": "https://static.fbcdn.net/a.js"}
                ]}

        result = last_valid_parent(stack)
        self.assertEqual(result["stack"]["callFrames"][0]["url"],\
                        "https://static.xx.fbcdn.net/rsrc.php/v4/y0/r/zzXQOjhbNNC.js")

    def test_last_valid_parent_with_parent(self):
        """Test last_valid_parent with parent specified and empty urls"""
        stack = {
            "callFrames": [{"url": ""}],
            "parent": {
                "callFrames": [{"url": "chrome://something"}],
                "parent": {
                    "callFrames": [{"url": "https://valid.example.com/script.js"}]
                }
            }
        }

        result = last_valid_parent(stack)
        self.assertEqual(result["stack"]["callFrames"][0]["url"],\
                            "https://valid.example.com/script.js")

    def test_last_valid_parent_empty(self):
        """Test no parent no valid URL"""
        stack = {"callFrames": [{"url": ""}]}

        result = last_valid_parent(stack)
        self.assertEqual(result, {"stack": {"callFrames": []}})

    def test_reduce_initiator_callstack(self):
        """Test that call stack is correctly reduced"""
        log = {"params": {"initiator": {"stack": {"callFrames":
                                    [{"url": "https://example.com/sc.js"},
                                    {"url": "https://next.example.com/a.js"}]},
                        "type": "script"}}}

        # Check callFrames is of size 1 with the valid member
        result = reduce_initiator_callstack(log)
        self.assertEqual(len(result["stack"]["callFrames"]), 1)
        self.assertEqual(result["stack"]["callFrames"][0]["url"], "https://example.com/sc.js")
        self.assertEqual(result["type"], "script")

        log = {"params": {"initiator": {"url": "https://example.com/sc.js"}}}

        # Check initiator is set correctly if no stack
        result = reduce_initiator_callstack(log)
        self.assertEqual(result["url"], "https://example.com/sc.js")

    def test_get_network_requests(self):
        """Test that network events are correctly obtained"""
        logs = [{"message": '{"message": {"method": "Network.requestWillBeSent", "params": \
        {"request": {"url": "https://a.test.com"}, "documentURL": "https://a.test.com",\
        "timestamp": 111, "requestId": "1", "loaderId": "1",\
        "initiator": {"url": "https://test.com/b.js", "type": "parser"}}}}'}]
        results = get_network_requests(logs, compact=False)

        # only one request
        self.assertEqual(len(results), 1)

        # Check its values seem good
        self.assertEqual(results[0]["requested_resource"], "https://a.test.com")
        self.assertEqual(results[0]["requested_for"], "https://a.test.com")
        self.assertEqual(results[0]["initiator"]["url"], "https://test.com/b.js")

    def test_get_network_requests_compact(self):
        """Test that network events are correctly obtained with compact"""
        logs = [{"message": '{"message": {"method": "Network.requestWillBeSent", "params": \
        {"request": {"url": "https://a.test.com"}, "documentURL": "https://a.test.com",\
        "timestamp": 111, "requestId": "1", "loaderId": "1",\
        "initiator": {"url": "https://test.com/b.js", "type": "parser"}}}}'}]
        results = get_network_requests(logs, compact=True)

        # only one request
        self.assertEqual(len(results), 1)

        # Check its values seem good
        self.assertEqual(results[0]["requested_resource"], "https://a.test.com")
        self.assertEqual(results[0]["requested_for"], "https://a.test.com")
        self.assertEqual(results[0]["initiator"]["url"], "https://test.com/b.js")

    def test_get_network_requests_skip(self):
        """Test that internal network events are skipped"""
        logs = [{"message": '{"message": {"method": "Network.requestWillBeSent", "params": \
        {"request": {"url": "https://a.test.com"}, "documentURL": "https://a.test.com",\
        "timestamp": 111, "requestId": "1", "loaderId": "1",\
        "initiator": {"url": "https://test.com/b.js", "type": "parser"}}}}'},
        {"message": '{"message": {"method": "Network.requestWillBeSent", "params": \
        {"request": {"url": "chrome://extension"}, "documentURL": "https://a.test.com",\
        "timestamp": 111, "requestId": "1", "loaderId": "1",\
        "initiator": {"url": "https://test.com/b.js", "type": "parser"}}}}'}
        ]
        results = get_network_requests(logs, compact=False)

        # only one request
        self.assertEqual(len(results), 1)

    # @patch replaces the argument of the following function with mock objects
    # first patch = last arg
    @patch("source.traffic_logger.network_logs_loader.setup_chrome_for_traffic_logging")
    @patch("source.traffic_logger.network_logs_loader.enable_developer_mode")
    def test_get_page_network_traffic(self, _, setup_chrome_for_traffic_logging):
        """Test that page network traffic is correctly obtained"""

        # Simulated driver
        mock_driver = MagicMock()

        # For get_log, returns this message
        mock_driver.get_log.return_value = \
        [{"message": '{"message": {"method": "Network.requestWillBeSent", "params": \
        {"request": {"url": "https://a.test.com"}, "documentURL": "https://a.test.com",\
        "timestamp": 111, "requestId": "1", "loaderId": "1",\
        "initiator": {"url": "https://test.com/b.js", "type": "parser"}}}}'}]

        # Return value of of setup_driver is mock_driver
        setup_chrome_for_traffic_logging.return_value = mock_driver

        # Mock class to mock Config
        class MockConfig:
            page_wait_time = 1

        # Check results contain expected value
        result = get_page_network_traffic("https://example.com", MockConfig(), compact=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["initiator"]["url"], "https://test.com/b.js")

    @patch("source.traffic_logger.network_logs_loader.setup_chrome_for_traffic_logging")
    @patch("source.traffic_logger.network_logs_loader.enable_developer_mode")
    def test_get_page_network_traffic_exception(self, _, setup_chrome_for_traffic_logging):
        """Test that page network traffic error is correctly raised"""

        # Simulated driver
        mock_driver = MagicMock()

        # Raise error
        mock_driver.get.side_effect = Exception("Test network collection error")

        # Return value of of setup_driver is mock_driver
        setup_chrome_for_traffic_logging.return_value = mock_driver

        # Mock class to mock Config
        class MockConfig:
            page_wait_time = 1

        result = get_page_network_traffic("https://example.com", MockConfig(), compact=True)

        # Error returns empty dict
        self.assertEqual(result, {})
        mock_driver.quit.assert_called_once()

    @patch("source.traffic_logger.network_logs_loader.WebDriverWait")
    def test_enable_developer_mode(self, mock_webdriver_wait):
        """Test that enable_developer_mode correctly works with Selenium"""

        mock_driver = MagicMock()
        mock_extensions_manager = MagicMock()
        mock_toolbar = MagicMock()
        mock_dev_mode_button = MagicMock()
        mock_update_button = MagicMock()

        mock_webdriver_wait.return_value.until.return_value = mock_extensions_manager
        mock_driver.find_element.return_value = mock_extensions_manager
        mock_extensions_manager.shadow_root = mock_toolbar
        mock_toolbar.shadow_root = mock_toolbar
        mock_toolbar.find_element.side_effect = lambda _, value:\
        {
            "toolbar": mock_toolbar,
            "devMode": mock_dev_mode_button,
            "updateNow": mock_update_button
        }[value]


        enable_developer_mode(mock_driver)

        mock_driver.get.assert_called_once_with("chrome://extensions")
        mock_webdriver_wait.return_value.until.assert_called_once()
        mock_toolbar.find_element.assert_any_call("id", "toolbar")
        mock_toolbar.find_element.assert_any_call("id", "devMode")
        mock_dev_mode_button.click.assert_called_once()
        mock_toolbar.find_element.assert_any_call("id", "updateNow")
        mock_driver.execute_script.assert_called_once_with("arguments[0].click();",\
                                                        mock_update_button)
