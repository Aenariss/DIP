# test_traffic_loader.py
# Test the traffic_loader.py is valid
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
from source.traffic_logger.traffic_loader import visit_page, save_traffic, delete_unsuccesfull_fpd
from source.traffic_logger.traffic_loader import match_jshelter_fpd, get_page_logs, load_traffic

class TestVisitPage(unittest.TestCase):
    @patch("source.traffic_logger.traffic_loader.get_page_network_traffic")
    def test_visit_page_success(self, mock_get_traffic):
        """Test visit_page with network traffic successfuly obtained"""
        mock_get_traffic.return_value = ["event_1", "event_2"]

        class MockConfig:
            page_wait_time = 1
        status, network_traffic = visit_page("https://example.com", MockConfig(), compact=False)

        self.assertTrue(status)
        self.assertEqual(network_traffic, ["event_1", "event_2"])

    @patch("source.traffic_logger.traffic_loader.get_page_network_traffic")
    def test_visit_page_empty_traffic(self, mock_get_traffic):
        """Test visit_page with no network traffic obtained"""
        mock_get_traffic.return_value = []  # Simulate an empty network log

        class MockConfig:
            page_wait_time = 1
        status, network_traffic = visit_page("https://example.com", MockConfig(), compact=False)

        self.assertFalse(status)  # Should return False when traffic is empty
        self.assertEqual(network_traffic, [])

    @patch("source.traffic_logger.traffic_loader.get_page_network_traffic")
    def test_visit_page_exception(self, mock_get_traffic):
        """Test visit_page with an exception"""
        mock_get_traffic.side_effect = Exception("Testing Exception for visit_page")

        class MockConfig:
            page_wait_time = 1
        status, network_traffic = visit_page("https://example.com", MockConfig(), compact=False)

        self.assertFalse(status)  # Should return False on exception
        self.assertEqual(network_traffic, [])

    @patch("builtins.open")
    @patch("json.dumps")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    def test_save_traffic_dns(self, mock_delete_fpd, mock_json_dumps, mock_open):
        """Test saving traffic success"""
        traffic_data = {'dns': True}
        save_traffic(traffic_data, "https://example.com", "1", "dns")
        mock_open.assert_called_once_with("./traffic/1_dns.json", "w", encoding="utf-8")
        mock_json_dumps.assert_called_once_with(traffic_data, indent=4)
        mock_open().write.assert_called_once()

    @patch("builtins.open")
    @patch("json.dumps")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    def test_save_traffic_network(self, mock_delete_fpd, mock_json_dumps, mock_open):
        """Test saving traffic success"""
        traffic_data = {'network': True}
        save_traffic(traffic_data, "https://example.com", "1", "network")
        mock_open.assert_called_once_with("./traffic/1_network.json", "w", encoding="utf-8")
        mock_json_dumps.assert_called_once_with(traffic_data, indent=4)
        mock_open().write.assert_called_once()

    @patch("builtins.open")
    @patch("builtins.exit")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    def test_save_traffic_error(self, mock_delete, mock_exit, mock_open):
        """Test save_traffic exception"""
        traffic_data = {'dns': True}
        mock_open.side_effect = Exception("Testing exception for save_traffic")

        self.assertRaises(BaseException,\
            save_traffic(traffic_data, "https://example.com", "0", "dns"))

        mock_exit.assert_called_once()
        mock_delete.assert_called_once()

    @patch("os.listdir")
    @patch("os.remove")
    def test_delete_unsuccessful_fpd(self, mock_remove, mock_listdir):
        """Test deleting unsuccessful FPD files"""
        mock_listdir.return_value = [".empty", "http_example_com.json"]
        delete_unsuccesfull_fpd()

        mock_remove.assert_called_once_with("./traffic/http_example_com.json")

    @patch("os.listdir")
    @patch("os.rename")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    def test_match_jshelter_fpd(self, mock_delete, mock_rename, mock_listdir):
        """Test matching JShelter FPD files"""
        mock_listdir.return_value = [".empty", "http_example_com.json"]
        match_jshelter_fpd(5)

        mock_rename.assert_called_once_with("./traffic/http_example_com.json",\
                                            "./traffic/5_fp.json")
        mock_delete.assert_called_once()

    @patch("os.listdir")
    @patch("builtins.exit")
    def test_match_jshelter_fpd_no_file(self, mock_exit, mock_listdir):
        """Test matching JSHelter FPD when no FPD file exists"""
        mock_listdir.return_value = [".empty"]
        mock_exit.side_effect = BaseException("JShelter did not match file!")

        with self.assertRaises(BaseException):
            match_jshelter_fpd(0)

        mock_exit.assert_called_once()

    @patch("source.traffic_logger.traffic_loader.visit_page")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    def test_get_page_logs_success(self, mock_sniffer_class, mock_visit):
        """Test successfully getting page logs"""
        mock_visit.return_value = (True, ["test_network_data"])
        mock_sniffer = mock_sniffer_class.return_value
        mock_sniffer.get_traffic.return_value = {"dns": "data"}

        dns, network = get_page_logs(mock_sniffer, "https://example.com", MagicMock(), compact=True)

        self.assertEqual(dns, {"dns": "data"})
        self.assertEqual(network, ["test_network_data"])
        mock_sniffer.start_sniffer.assert_called_once()
        mock_sniffer.stop_sniffer.assert_called_once()

    @patch("source.traffic_logger.traffic_loader.visit_page")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    def test_get_page_logs_failure(self, mock_sniffer_class, mock_visit):
        """Test error in get_page_logs"""
        mock_visit.return_value = (False, [])
        mock_sniffer = mock_sniffer_class.return_value

        dns, network = get_page_logs(mock_sniffer, "https://example.com", MagicMock(), compact=True)

        self.assertEqual(dns, {})
        self.assertEqual(network, [])
        mock_sniffer.stop_sniffer.assert_called_once()

    @patch("source.traffic_logger.traffic_loader.load_pages")
    @patch("source.traffic_logger.traffic_loader.get_page_logs")
    @patch("source.traffic_logger.traffic_loader.save_traffic")
    @patch("source.traffic_logger.traffic_loader.match_jshelter_fpd")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    @patch("source.traffic_logger.traffic_loader.is_dns_valid")
    def test_load_traffic_success(self, mock_validity, mock_sniffer_class, mock_delete, mock_match,\
                                mock_save, mock_get_logs, mock_load_pages):
        """Test full load_traffic"""
        mock_get_logs.return_value = ({'dns': 'data'}, ["https://example.com"])
        mock_load_pages.return_value = ["https://example.com"]
        mock_validity.return_value = True, mock_get_logs.return_value
        class MockConfig:
            max_repeat_log_attempts = 2
            no_dns_validation_during_logging = False

        load_traffic(MockConfig(), compact=False)

        mock_load_pages.assert_called_once()
        mock_get_logs.assert_called_once()
        mock_save.assert_called()
        mock_match.assert_called()
        mock_validity.assert_called_once()

    @patch("source.traffic_logger.traffic_loader.load_pages")
    @patch("source.traffic_logger.traffic_loader.get_page_logs")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    @patch("source.traffic_logger.traffic_loader.is_dns_valid")
    def test_load_traffic_no_network(self, mock_validity, mock_sniffer_class, mock_delete, mock_get_logs,\
                                    mock_load_pages):
        """Test load_traffic when network logging returns {}"""
        mock_get_logs.return_value = ({}, [])
        mock_validity.return_value = True, mock_get_logs.return_value
        mock_load_pages.return_value = ["https://example.com"]
        class MockConfig:
            max_repeat_log_attempts = 2
            no_dns_validation_during_logging = False

        load_traffic(MockConfig(), compact=False)

        mock_load_pages.assert_called_once()
        mock_get_logs.assert_called_once()
        mock_delete.assert_called()
        mock_validity.assert_called_once()

    @patch("source.traffic_logger.traffic_loader.load_pages")
    @patch("source.traffic_logger.traffic_loader.get_page_logs")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    @patch("source.traffic_logger.traffic_loader.is_dns_valid")
    def test_load_traffic_no_validity_checking(self, mock_validity, mock_sniffer_class, mock_delete,\
                                            mock_get_logs, mock_load_pages):
        """Test load_traffic when validity checkinng is turned off"""
        mock_get_logs.return_value = ({}, [])
        mock_load_pages.return_value = ["https://example.com"]
        class MockConfig:
            max_repeat_log_attempts = 2
            no_dns_validation_during_logging = True

        load_traffic(MockConfig(), compact=False)

        mock_load_pages.assert_called_once()
        mock_get_logs.assert_called_once()
        mock_delete.assert_called()
        mock_validity.assert_not_called()

    @patch("source.traffic_logger.traffic_loader.load_pages")
    @patch("source.traffic_logger.traffic_loader.get_page_logs")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    @patch("source.traffic_logger.traffic_loader.is_dns_valid")
    def test_load_traffic_validity_error(self, mock_validity, mock_sniffer_class, mock_delete,\
                                        mock_get_logs, mock_load_pages):
        """Test load_traffic when validity check returns an error"""
        mock_get_logs.return_value = ({}, ["network_something"])
        mock_load_pages.return_value = ["https://example.com"]
        mock_validity.return_value = False, {}
        class MockConfig:
            max_repeat_log_attempts = 2
            no_dns_validation_during_logging = False

        load_traffic(MockConfig(), compact=False)

        mock_load_pages.assert_called_once()

        # All of these should be called three times cuz of 2 repeat attempts
        self.assertEqual(mock_delete.call_count, 3)
        self.assertEqual(mock_get_logs.call_count, 3)
        self.assertEqual(mock_validity.call_count, 3)

    @patch("source.traffic_logger.traffic_loader.load_pages")
    @patch("source.traffic_logger.traffic_loader.get_page_logs")
    @patch("source.traffic_logger.traffic_loader.delete_unsuccesfull_fpd")
    @patch("source.traffic_logger.traffic_loader.DNSSniffer")
    @patch("source.traffic_logger.traffic_loader.is_dns_valid")
    def test_load_traffic_network_error_on_repeat(self, mock_validity, mock_sniffer_class,\
                                                mock_delete, mock_get_logs, mock_load_pages):
        """Test load_traffic when network data is loaded for the first but not second time"""
        mock_get_logs.side_effect = [({}, ["network_something"]), ({}, []), ({}, ["network_something"])]
        mock_load_pages.return_value = ["https://example.com"]
        mock_validity.return_value = False, {}
        class MockConfig:
            max_repeat_log_attempts = 2
            no_dns_validation_during_logging = False

        load_traffic(MockConfig(), compact=False)

        mock_load_pages.assert_called_once()

        # All of these should be called three times cuz of 2 repeat attempts
        self.assertEqual(mock_delete.call_count, 3)
        self.assertEqual(mock_get_logs.call_count, 3)
        self.assertEqual(mock_validity.call_count, 3)
