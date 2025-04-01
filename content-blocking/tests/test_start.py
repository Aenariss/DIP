# test_start.py
# Test the high-level control functions used in start.py
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
from unittest.mock import patch

# Custom modules
from start import initialize_folders, check_traffic_folder, obtain_data, parse_traffic
from start import obtain_simulation_results, analyze_results, start

class TestStart(unittest.TestCase):
    
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open")
    def test_initialize_folders_creates_traffic_folder(self, mock_open, mock_exists, mock_makedirs):
        initialize_folders()
        mock_makedirs.assert_called_with("traffic/")