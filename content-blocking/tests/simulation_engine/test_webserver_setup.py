# test_webserver_setup.py
# Test the functions used in simulation_server_setup from simulation_engine
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
import source.simulation_engine.simulation_server_setup
from source.simulation_engine.simulation_server_setup import start_testing_server, run_test_server
from source.simulation_engine.simulation_server_setup import stop_testing_server
from source.simulation_engine.simulation_server_setup import app

class TestFlaskServer(unittest.TestCase):

    def setUp(self):
        """Method to initialize the offline client"""
        self.client = app.test_client()

    def test_index_with_resources(self):
        """Test index function"""
        source.simulation_engine.simulation_server_setup.list_of_resources = \
            ["https://example.com/", "https://test.cz/"]
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("https://example.com/", response.get_data(as_text=True))
        self.assertIn("https://test.cz/", response.get_data(as_text=True))
        self.assertIn("let total_resources = 2", response.get_data(as_text=True))

    def test_index_without_resources(self):
        """Test index function when empty resources"""
        source.simulation_engine.simulation_server_setup.list_of_resources = []
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("let total_resources = 0", response.text)

    @patch("source.simulation_engine.simulation_server_setup.app.run")
    def test_run_test_server(self, mock_run):
        """Test run_test_server"""
        test_resources = ["https://example.com/"]
        run_test_server(test_resources)
        self.assertEqual(source.simulation_engine.simulation_server_setup.list_of_resources,\
                        test_resources)
        mock_run.assert_called_once_with(port=5000, use_reloader=False)

    @patch("source.simulation_engine.simulation_server_setup.Process")
    @patch("source.simulation_engine.simulation_server_setup.app.run")
    def test_start_testing_server(self, mock_run, mock_process):
        """Test starting the server"""
        mock_proc_instance = MagicMock()
        mock_process.return_value = mock_proc_instance

        test_resources = ["https://example.com/"]
        server = start_testing_server(test_resources)

        self.assertEqual(server, mock_proc_instance)
        mock_process.assert_called_once_with(target=run_test_server, args=(test_resources,))
        mock_proc_instance.start.assert_called_once()

    @patch("source.simulation_engine.simulation_server_setup.Process")
    def test_server_stop(self, mock_process):
        """Test stopping the server"""
        mock_proc_instance = MagicMock()
        stop_testing_server(mock_proc_instance)

        mock_proc_instance.terminate.assert_called_once()
        mock_proc_instance.join.assert_called_once()
