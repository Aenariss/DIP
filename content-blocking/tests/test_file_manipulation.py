# test_file_manipulation.py
# Test file manipulaiton operations
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
from unittest.mock import patch, mock_open

# Custom modules
from source.file_manipulation import load_json, save_json, load_pages, get_traffic_files

class TestFileManipulation(unittest.TestCase):

    @patch("builtins.open", mock_open(read_data="http://example.com\nhttp://test.com\n"))
    def test_load_pages(self):
        """Test load_pages correctly parses the input. Uses mock_open inside the patch decorator,
        read_data provides the text that is returned upon open()"""
        expected = ["http://example.com", "http://test.com"]
        self.assertEqual(load_pages(), expected)

    @patch("builtins.open")
    def test_load_pages_file_not_found(self, mock_open_function):
        mock_open_function.side_effect = OSError()
        with self.assertRaises(SystemExit):
            load_pages()

    @patch("builtins.open", mock_open(read_data='{"key": "value"}'))
    def test_load_json(self):
        expected = {"key": "value"}
        self.assertEqual(load_json("test.json"), expected)

    @patch("builtins.open")
    def test_load_json_file_not_found(self, mock_open_function):
        mock_open_function.side_effect = OSError()
        with self.assertRaises(SystemExit):
            load_json("test.json")

    @patch("builtins.open", mock_open())
    @patch("json.dump")
    def test_save_json(self, mock_json_dump):
        data = {"key": "value"}
        save_json(data, "test.json")
        mock_json_dump.assert_called_once()

    @patch("builtins.open")
    def test_save_json_file_error(self, mock_open_function):
        mock_open_function.side_effect = OSError()
        with self.assertRaises(SystemExit):
            save_json({"key": "value"}, "test.json")

    @patch("os.listdir")
    def test_get_traffic_files(self, mock_listdir):
        mock_listdir.return_value = ["1_fp.json", "1_dns.json", "1_network.json", ".empty"]
        files = get_traffic_files('dns')
        self.assertIn("./traffic/1_dns.json", files)

    @patch("os.listdir")
    def test_get_traffic_files_error(self, mock_listdir):
        mock_listdir.return_value =["1_fp.json", "1_dns.json", "1_network.json", ".empty"]
        with self.assertRaises(SystemExit):
            _ = get_traffic_files('something_random')
