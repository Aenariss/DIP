# test_analysis_utils.py
# Test functions in analysis_utils.py from Analysis Engine
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
from source.traffic_parser.create_request_trees import reconstruct_tree
from source.analysis_engine.analysis_utils import get_directly_blocked_tree
from source.analysis_engine.analysis_utils import get_transitively_blocked_tree
from source.analysis_engine.analysis_utils import parse_console_logs_chrome
from source.analysis_engine.analysis_utils import process_firefox_console_output
from source.file_manipulation import load_json


class TestAnalysisUtils(unittest.TestCase):
    def setUp(self):
        self.traffic_file = load_json("./tests/analysis_engine/example_network_traffic.json")
        self.request_tree = reconstruct_tree(self.traffic_file, {}, False)
        self.blocked_requests = ["https://b.cz/asc.js", "https://loaded-twice.cz/script.js"]

    def test_get_directly_blocked_tree(self):
        """Test that blocking occurs as it should"""
        result_tree = get_directly_blocked_tree(self.request_tree, self.blocked_requests)

        for node in self.blocked_requests:
            found_nodes = result_tree.find_nodes(node)
            for found_node in found_nodes:
                self.assertTrue(found_node.is_blocked())

    def test_get_transitively_blocked_tree(self):
        """Test transitive blocking works as it should"""

        # Block second root node, so basically everything but the get_root()
        blocked_requests = ["https://www.a.cz/"]
        result_tree = get_transitively_blocked_tree(self.request_tree, blocked_requests)

        for node in result_tree.get_root().get_all_children_nodes():
            if node == result_tree.get_root():
                # Only root node is not blocked
                self.assertFalse(node.is_blocked())
            else:
                self.assertTrue(node.is_blocked())

    def test_get_transitively_blocked_tree_repeated(self):
        """Test transitive blocking works as it should"""

        # Mark blocked node as repeated
        blocked_requests = ["https://www.a.cz/"]
        blocked_node = self.request_tree.find_nodes(blocked_requests[0])[0]
        blocked_node.repeated = True
        result_tree = get_transitively_blocked_tree(self.request_tree, blocked_requests)

        # Since root node was repeated, only that node should be blocked
        self.assertTrue(blocked_node.is_blocked())

        # Its children should not be blocked since they might have been assigned somewhere else
        for node in result_tree.get_root().get_all_children_nodes():

            # Assert all but the blocked node are not blocked
            if node != blocked_node:
                self.assertFalse(node.is_blocked())

    def test_parse_console_logs_chrome(self):
        """Test Chrome log parsing"""
        console_output = [
            {"level": "SEVERE", "message": "https://example.com/script.js ERR_BLOCKED_BY_CLIENT"},
            {"level": "INFO", "message": "Some other log"},
        ]
        blocked_resources = parse_console_logs_chrome(console_output)
        self.assertEqual(blocked_resources, ["https://example.com/script.js"])

    def test_parse_console_logs_chrome_invalid(self):
        """Test Chrome log parsing with invalid message format"""
        console_output = [{"level": "SEVERE", "message": ""}]
        blocked_resources = parse_console_logs_chrome(console_output)
        self.assertEqual(blocked_resources, [])

    @patch("source.analysis_engine.analysis_utils.squash_tree_resources")
    def test_process_firefox_console_output(self, mock_tree_resources):
        """Test firefox log parsing"""
        request_trees = {"1_network.json": self.request_tree}
        all_requests = self.request_tree.get_all_requests()

        mock_tree_resources.return_value = all_requests

        all_request_but_one = all_requests[1:]
        blocked_resources = process_firefox_console_output(request_trees, all_request_but_one)

        self.assertEqual(blocked_resources, [all_requests[0]])

    @patch("source.analysis_engine.analysis_utils.squash_tree_resources")
    def test_process_firefox_console_output_internals(self, mock_tree_resources):
        """Test firefox log parsing with internal requests"""
        request_trees = {"1_network.json": self.request_tree}
        all_requests = self.request_tree.get_all_requests()
        all_requests.append("blob://example.com")
        all_requests.append("data:abcd45")
        all_requests.append("about:blank")
        all_requests.append("chrome://extension")
        all_requests.append("chrome-something://extension")

        mock_tree_resources.return_value = all_requests

        all_request_but_one = all_requests[1:]
        blocked_resources = process_firefox_console_output(request_trees, all_request_but_one)

        self.assertEqual(blocked_resources, [all_requests[0]])
