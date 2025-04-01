# test_utils.py
# Test utils work correctly
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
from unittest.mock import patch, MagicMock, call, mock_open

from source.utils import print_progress, squash_dns_records, squash_tree_resources
from source.utils import add_substract_fp_attempts

class TestUtils(unittest.TestCase):

    @patch("builtins.print")
    def test_print_progress(self, mock_print):
        """Test progress printing works"""
        progress_func = print_progress(100, "Progress:", limiter=20)
        for _ in range(100):
            progress_func()

        expected_prints = [
            call("Progress:", "20.0%"),
            call("Progress:", "40.0%"),
            call("Progress:", "60.0%"),
            call("Progress:", "80.0%"),
            call("Progress:", "100.0%")
        ]
        mock_print.assert_has_calls(expected_prints)

    @patch("builtins.open", new_callable=mock_open)
    @patch("source.utils.get_traffic_files")
    def test_squash_dns_records(self, mock_get_traffic_files, mock_open_instance):
        """Test DNS resources squashing"""
        mock_get_traffic_files.return_value=["1_dns.json", "2_dns.json"]
        mock_open_instance.side_effect = [
            mock_open(read_data='{"example.com": {"www": {"A": ["192.168.0.1"]}}}').return_value,
            mock_open(read_data='{"example.com": {"mail": {"A": ["192.168.1.1"]}}}').return_value,
        ]

        expected_result = {
            "example.com": 
                {
                    "www": {
                        "A": ["192.168.0.1"]
                    },
                    "mail": {
                        "A": ["192.168.1.1"]
                    }
                }
        }

        result = squash_dns_records()
        self.assertEqual(result, expected_result)

        # Called for both files 1_dns and 2_dns
        self.assertEqual(mock_open_instance.call_count, 2)
        mock_get_traffic_files.assert_called_once_with('dns')

    def test_squash_tree_resources(self):
        """Test tree resources are squashed correctly"""
        request_tree_1 = MagicMock()
        request_tree_1.get_all_requests.return_value = ["https://test.cz", "https://example.com"]

        request_tree_2 = MagicMock()
        request_tree_2.get_all_requests.return_value = ["https://example.com", "https://new.com"]

        request_trees = {"1_network.json": request_tree_1, "2_network.json": request_tree_2}
        expected_result = ["https://test.cz", "https://example.com", "https://new.com"]
        result = squash_tree_resources(request_trees)
        self.assertEqual(result, expected_result)

    def test_add_substract_fp_attempts_add(self):
        callers_1 = {"BrowserProperties": 10, "AlgorithmicMethods": 20}
        callers_2 = {"BrowserProperties": 5, "AlgorithmicMethods": 15}
        expected_result = {"BrowserProperties": 15, "AlgorithmicMethods": 35}
        result = add_substract_fp_attempts(callers_1, callers_2, add=True)
        self.assertEqual(result, expected_result)

    def test_add_substract_fp_attempts_subtract(self):
        callers_1 = {"BrowserProperties": 10, "AlgorithmicMethods": 20}
        callers_2 = {"BrowserProperties": 5, "AlgorithmicMethods": 15}
        expected_result = {"BrowserProperties": 5, "AlgorithmicMethods": 5}
        result = add_substract_fp_attempts(callers_1, callers_2, add=False)
        self.assertEqual(result, expected_result)

    def test_add_substract_fp_attempts_empty_dict(self):
        callers_1 = {"BrowserProperties": 10, "AlgorithmicMethods": 20}
        callers_2 = {}
        result = add_substract_fp_attempts(callers_1, callers_2, add=False)
        self.assertEqual(result, callers_1)

    def test_add_substract_fp_attempts_int_compatibility(self):
        callers_1 = {"BrowserProperties": 10, "AlgorithmicMethods": 20}
        result = add_substract_fp_attempts(5, callers_1, add=True)
        self.assertEqual(result, callers_1)

        result = add_substract_fp_attempts(callers_1, 5, add=True)
        self.assertEqual(result, callers_1)
