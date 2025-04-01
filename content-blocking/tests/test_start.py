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
from unittest.mock import patch, MagicMock
import sys
import subprocess

# Custom modules
from start import initialize_folders, check_traffic_folder, obtain_data, parse_traffic
from start import obtain_simulation_results, analyze_results, start

class TestStart(unittest.TestCase):
    
    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("builtins.open")
    @patch("os.remove")
    def test_initialize_folders_exists(self, mock_remove, mock_open, mock_exists,\
                                mock_makedirs):
        """Test initialize folder when the folder already exists"""
        mock_args = MagicMock()
        mock_args.load = True
        mock_args.load_only = False
        mock_exists.return_value = True

        initialize_folders(mock_args)
        mock_remove.assert_called()

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("builtins.open")
    @patch("os.remove")
    def test_initialize_folders_doesnt_exists(self, mock_remove, mock_open, mock_exists,\
                                mock_makedirs):
        """TEst initialize folders when the folder doesnt exist"""
        mock_args = MagicMock()
        mock_args.load = True
        mock_args.load_only = False
        mock_exists.return_value = False

        initialize_folders(mock_args)
        mock_makedirs.assert_called_once()

    @patch("start.args")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("os.path.isfile")
    def test_check_traffic_folder(self, mock_isfile, mock_listdir, mock_exists, mock_args):
        """Test when traffic folder exists but is empty"""
        mock_args = MagicMock()
        mock_args.load_only = False
        mock_isfile.return_value = True
        mock_listdir.return_value = [".empty"]
        mock_exists.return_value = True

        # Should crash since only 1 file exists (not enough for parsing)
        with self.assertRaises(SystemExit):
            check_traffic_folder()

    @patch("start.args")
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("os.path.isfile")
    def test_check_traffic_folder_not_exists(self, mock_isfile, mock_listdir, mock_exists, mock_args):
        """Test when traffic folder doesnt exist"""
        mock_args = MagicMock()
        mock_args.load_only = False
        mock_isfile.return_value = True
        mock_listdir.return_value = [".empty"]
        mock_exists.return_value = False

        # Should crash since folder doesnt exist
        with self.assertRaises(SystemExit):
            check_traffic_folder()

    @patch("start.load_traffic")
    def test_obtain_data_load(self, mock_load_traffic):
        """Test obtain data with --load"""
        mock_args = MagicMock()
        mock_args.load = True
        mock_args.load_only = False

        mock_config = MagicMock()
        result = obtain_data(mock_config, mock_args)

        self.assertFalse(result)

    @patch("start.load_traffic")
    def test_obtain_data_load_only(self, mock_load_traffic):
        """Test obtain data with --load-only"""
        mock_args = MagicMock()
        mock_args.load_only = True
        mock_args.load = False

        mock_config = MagicMock()
        result = obtain_data(mock_config, mock_args)

        self.assertTrue(result)

    @patch("start.load_traffic")
    def test_obtain_data_load_only_load(self, mock_load_traffic):
        """Test obtain data with --load-only and --load"""
        mock_args = MagicMock()
        mock_args.load = True
        mock_args.load_only = True

        mock_config = MagicMock()

        with self.assertRaises(SystemExit):
            result = obtain_data(mock_config, mock_args)

    @patch('start.check_traffic_folder')
    @patch('start.parse_fp')
    @patch('start.create_trees')
    def test_parse_traffic(self, mock_create_trees, mock_parse_fp, mock_check_traffic):
        """Test parse_traffic works"""
        mock_config = MagicMock()
        mock_create_trees.return_value = {"1_network.json": {"tree": True}}
        mock_parse_fp.return_value = {"1_network.json": True}

        result = parse_traffic(mock_config)
        self.assertIn("1_network.json", result)

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('start.load_json')
    @patch('start.save_json')
    @patch('start.squash_dns_records')
    @patch('start.squash_tree_resources')
    @patch('start.DNSRepeater')
    @patch('start.start_testing_server')
    @patch('start.firewall_block_traffic')
    @patch('start.visit_test_server')
    @patch('start.stop_testing_server')
    @patch('start.firewall_unblock_traffic')
    def test_obtain_simulation_results_analysis_only(self, mock_firewall_unblock,\
                                    mock_stop_testing, mock_visit_test, mock_firewall_block,\
                                    mock_start_testing, mock_dns_repeater, mock_squash_tree,\
                                    mock_squash_dns, mock_save_json, mock_load_json, mock_exists,\
                                    mock_makedirs):
        """Test obtain_simulation_results with analysis_only argument"""
        mock_load_json.return_value = {"not_empty": True}
        #mock_visit_test.return_value = {"not_empty": True}

        mock_args = MagicMock()
        mock_args.analysis_only = True
        mock_args.simulation_only = False

        mock_config = MagicMock()
        mock_request_trees = MagicMock()

        result = obtain_simulation_results(mock_request_trees, mock_config, mock_args)
        
        self.assertIsNotNone(result)

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('start.load_json')
    @patch('start.save_json')
    @patch('start.squash_dns_records')
    @patch('start.squash_tree_resources')
    @patch('start.DNSRepeater')
    @patch('start.start_testing_server')
    @patch('start.firewall_block_traffic')
    @patch('start.visit_test_server')
    @patch('start.stop_testing_server')
    @patch('start.firewall_unblock_traffic')
    def test_obtain_simulation_results_simulation_only(self, mock_firewall_unblock,\
                                    mock_stop_testing, mock_visit_test, mock_firewall_block,\
                                    mock_start_testing, mock_dns_repeater, mock_squash_tree,\
                                    mock_squash_dns, mock_save_json, mock_load_json, mock_exists,\
                                    mock_makedirs):
        """Test obtain_simulation_results with simulation_only argument"""
        #mock_load_json.return_value = {"not_empty": True}
        mock_visit_test.return_value = {"not_empty": True}
        mock_exists.return_value = False

        mock_args = MagicMock()
        mock_args.analysis_only = False
        mock_args.simulation_only = True

        mock_config = MagicMock()
        mock_request_trees = MagicMock()

        result = obtain_simulation_results(mock_request_trees, mock_config, mock_args)

        mock_makedirs.assert_called_once()
        self.assertIsNotNone(result)

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('start.load_json')
    @patch('start.save_json')
    @patch('start.squash_dns_records')
    @patch('start.squash_tree_resources')
    @patch('start.DNSRepeater')
    @patch('start.start_testing_server')
    @patch('start.firewall_block_traffic')
    @patch('start.visit_test_server')
    @patch('start.stop_testing_server')
    @patch('start.firewall_unblock_traffic')
    def test_obtain_simulation_results_exception(self, mock_firewall_unblock,\
                                    mock_stop_testing, mock_visit_test, mock_firewall_block,\
                                    mock_start_testing, mock_dns_repeater, mock_squash_tree,\
                                    mock_squash_dns, mock_save_json, mock_load_json, mock_exists,\
                                    mock_makedirs):
        """Test obtain_simulation_results which throws an exception during simulation"""
        mock_visit_test.side_effect = Exception()
        mock_exists.return_value = False

        mock_args = MagicMock()
        mock_args.analysis_only = False
        mock_args.simulation_only = True

        mock_config = MagicMock()
        mock_request_trees = MagicMock()

        with self.assertRaises(SystemExit):
            obtain_simulation_results(mock_request_trees, mock_config, mock_args)

        mock_firewall_unblock.assert_called_once()
        mock_stop_testing.assert_called_once()

    @patch("start.analyze_trees")
    @patch("start.save_json")
    def test_analyze_results(self, mock_save_json, mock_analyze_trees):
        """Test analyze_results"""
        mock_config = MagicMock()
        mock_console_output = []
        mock_request_trees = {}

        analyze_results(mock_request_trees, mock_console_output, mock_config)
        mock_save_json.assert_called_once()

    @patch("start.initialize_folders")
    @patch("start.obtain_data")
    @patch("start.parse_traffic")
    @patch("start.obtain_simulation_results")
    @patch("start.analyze_results")
    def test_start(self, mock_analyze_results, mock_obtain_results,\
                    mock_parse_traffic, mock_obtain_data, mock_initialize):
        """Test start function"""

        mock_obtain_data.return_value = False

        start(analysis_only=True)
        mock_initialize.assert_called_once()
        mock_obtain_data.assert_called_once()
        mock_parse_traffic.assert_called_once()
        mock_analyze_results.assert_called_once()

    @patch("start.initialize_folders")
    @patch("start.obtain_data")
    @patch("start.parse_traffic")
    @patch("start.obtain_simulation_results")
    @patch("start.analyze_results")
    def test_start_obtain_only(self, mock_analyze_results, mock_obtain_results,\
                    mock_parse_traffic, mock_obtain_data, mock_initialize):
        """Test start function"""

        mock_obtain_data.return_value = True

        start(analysis_only=True)
        mock_initialize.assert_called_once()
        mock_obtain_data.assert_called_once()
        mock_parse_traffic.assert_not_called()
        mock_analyze_results.assert_not_called()

    @patch("start.args")
    @patch("start.initialize_folders")
    @patch("start.obtain_data")
    @patch("start.parse_traffic")
    @patch("start.obtain_simulation_results")
    @patch("start.analyze_results")
    def test_start_simulation_only(self, mock_analyze_results, mock_obtain_results,\
                    mock_parse_traffic, mock_obtain_data, mock_initialize, mock_args):
        """Test start function"""

        mock_obtain_data.return_value = False
        mock_args.simulation_only = True

        start(analysis_only=True)
        mock_initialize.assert_called_once()
        mock_obtain_data.assert_called_once()
        mock_parse_traffic.assert_called_once()
        mock_analyze_results.assert_not_called()

    @patch("start.initialize_folders")
    @patch("start.obtain_data")
    @patch("start.parse_traffic")
    @patch("start.obtain_simulation_results")
    @patch("start.analyze_results")
    def test_start_invalid_config(self, mock_analyze_results, mock_obtain_results,\
                    mock_parse_traffic, mock_obtain_data, mock_initialize):
        """Test start function"""
        mock_config = MagicMock()
        mock_config.validate_settings.return_value = False

        with self.assertRaises(SystemExit):
            start(mock_config, analysis_only=True)
