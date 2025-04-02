# test_create_request_trees.py
# Test the create_request_trees.py from traffic_parser
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
from source.traffic_parser.request_node import RequestNode
from source.traffic_parser.request_tree import RequestTree
from source.traffic_parser.create_request_trees import fix_missing_parent, join_call_frames
from source.traffic_parser.create_request_trees import assign_parent_from_callstack
from source.traffic_parser.create_request_trees import add_new_root_node, assign_direct_parent
from source.traffic_parser.create_request_trees import create_trees, load_network_traffic_files
from source.traffic_parser.create_request_trees import has_direct_initiator, has_stack_specified
from source.traffic_parser.create_request_trees import is_root_node
from source.file_manipulation import load_json

class TestcreateRequestTrees(unittest.TestCase):

    def setUp(self):
        """Load custom network traffic file for testing"""
        self.traffic = load_json("./tests/traffic_parser/example_network_traffic.json")

        self.root_node = RequestNode(0, "https://example.com", {})
        self.root_node.root_node =  True
        self.child_node = RequestNode(1, "https://example.com/script.js", {})
        self.tree = RequestTree(self.root_node)
        self.root_node.add_child(self.child_node)

        self.test_network_traffic_file = "log_1_network.json"

        # Parsed FP attempts to assign, simplified
        self.parsed_fp_attempts = \
            {self.test_network_traffic_file: \
            {'<anonymous>': {'BrowserProperties': 4, 'AlgorithmicMethods': 0},
            'https://loaded-twice.cz/script.js': {'BrowserProperties': 6, 'AlgorithmicMethods': 0},
            'https://two-parents.cz/script.js': {'BrowserProperties': 2, 'AlgorithmicMethods': 0},
            'https://b.cz/asc.js': {'BrowserProperties': 1, 'AlgorithmicMethods': 0},
            'https://example.com/script.js': {'BrowserProperties': 1, 'AlgorithmicMethods': 0},
            }}

    def test_is_root_node_valid(self):
        """Test if checker if node is a root-node works"""
        root_resource = {
            "requested_for": "https://test.com",
            "requested_resource": "https://test.com",
            "initiator": {
                "type": "other"
            }
        }
        self.assertTrue(is_root_node(root_resource))

    def test_is_root_node_invalid(self):
        """Test if checker if invalid node gets rejected as root"""
        root_resource_invalid = {
            "requested_for": "https://test.com",
            "requested_resource": "https://test.com",
            "initiator": {
                "type": "other",
                "url": "https://something.com"
            }
        }

        regular_node = {
            "requested_for": "https://test.com",
            "requested_resource": "https://something-else.com",
            "initiator": {
                "type": "other",
                "url": "https://something.com"
            }
        }
        self.assertFalse(is_root_node(root_resource_invalid))
        self.assertFalse(is_root_node(regular_node))

    def test_has_direct_initiator(self):
        """Test if checker if node has direct initiator works"""
        resource_no_url = {
            "requested_for": "https://test.com",
            "requested_resource": "https://something-else.com",
            "initiator": {
                "type": "parser"
            }
        }
        self.assertFalse(has_direct_initiator(resource_no_url))

        # Assign it valid initiator.url, should now work
        resource_no_url["initiator"]["url"] = "https://specified-parent.com"

        self.assertTrue(has_direct_initiator(resource_no_url))

    def test_has_stack_specified(self):
        """Test if checker if node has stack specified works"""
        resource_no_stack = {
            "requested_for": "https://test.com",
            "requested_resource": "https://something-else.com",
            "initiator": {
                "type": "script",
            }
        }
        self.assertFalse(has_stack_specified(resource_no_stack))

        # Assign it valid stack, should now work
        resource_no_stack["initiator"]["stack"] = \
            {"stack": {
                "callFrames": [{"url": "https://b.cz/sc.js"}]
                }
            }
        self.assertTrue(has_stack_specified(resource_no_stack))

    def test_fix_missing_parent(self):
        """Test fix_missing_parent correctly assigns node as child of root node"""
        fix_missing_parent(self.root_node, self.child_node)
        self.assertIn(self.child_node, self.root_node.children)

    def test_join_call_frames_no_parent(self):
        """Test call frames are being joined correctly"""
        stack = {"callFrames": [
            {"url": "chrome-extension://nn/test"},
            {"url": "https://b.cz/sc.js"},
            {"url": "https://b.cz/sc.js"}]}

        result = join_call_frames(stack)
        expected = ["https://b.cz/sc.js",\
                    "https://b.cz/sc.js", "chrome-extension://nn/test"]
        self.assertEqual(result, expected)

    def test_join_call_frames_parent(self):
        """Test call frames are being joined correctly with parent attribute present"""
        stack = {"parent": {
            "callFrames": 
            [{"url": "https://parent.com/b.js"},
            {"url": "https://parent.com/a.js"}]
        },
            "callFrames": [
            {"url": "chrome-extension://nn/test"},
            {"url": "https://b.cz/sc.js"},
            {"url": "https://b.cz/sc.js"}]}

        result = join_call_frames(stack)
        expected = ["https://parent.com/a.js", "https://parent.com/b.js", "https://b.cz/sc.js",\
                    "https://b.cz/sc.js", "chrome-extension://nn/test"]
        self.assertEqual(result, expected)

    def test_add_new_root_node_first_request(self):
        """Test adding new node when it's the first requestt correctly creates tree"""
        fp_attempts = self.parsed_fp_attempts[self.test_network_traffic_file]
        new_root_node = RequestNode(1, "https://example.com/script.js",\
                                    fp_attempts.get("https://example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(None, 0, new_root_node, None,\
                                                            fp_attempts, False)

        self.assertIsInstance(tree, RequestTree)
        self.assertEqual(current_root_node, new_root_node)
        self.assertTrue(current_root_node.root_node)
        self.assertEqual(tree.get_root(), new_root_node)

        # Check it was assigned anonymous FP attempts + its own 1 attempts
        fp_attempts = new_root_node.get_fp_attempts()
        expected = {"BrowserProperties": 5, "AlgorithmicMethods": 0}
        self.assertEqual(fp_attempts, expected)

    def test_add_new_root_node_after(self):
        """Test adding new node when previous root node exists"""
        fp_attempts = self.parsed_fp_attempts[self.test_network_traffic_file]
        new_root_node = RequestNode(1, "https://example.com/script.js",\
                                    fp_attempts.get("https://example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(None, 0, new_root_node, None,\
                                                            fp_attempts, False)

        second_root_node = RequestNode(2, "https://www.example.com/script.js",\
                                    fp_attempts.get("https://www.example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(tree, 1, second_root_node, current_root_node,\
                                    fp_attempts, False)

        self.assertEqual(current_root_node, second_root_node)
        self.assertTrue(current_root_node.root_node)

        # Check previous root node was deleted all anonymous FP attempts
        fp_attempts = new_root_node.get_fp_attempts()
        expected = {"BrowserProperties": 1, "AlgorithmicMethods": 0}
        self.assertEqual(fp_attempts, expected)

        # Check new root node was assigned anonymous FP attempts
        fp_attempts = current_root_node.get_fp_attempts()
        expected = {"BrowserProperties": 4, "AlgorithmicMethods": 0}
        self.assertEqual(fp_attempts, expected)

    def test_add_new_root_node_twice(self):
        """Test adding new root node when same root node exists adds it as child"""
        fp_attempts = self.parsed_fp_attempts[self.test_network_traffic_file]
        new_root_node = RequestNode(1, "https://example.com/script.js",\
                                    fp_attempts.get("https://example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(None, 0, new_root_node, None,\
                                                            fp_attempts, False)

        same_root_node = RequestNode(2, "https://example.com/script.js",\
                                    fp_attempts.get("https://example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(tree, 1, same_root_node, current_root_node,\
                                    fp_attempts, False)

        self.assertEqual(current_root_node, new_root_node)
        self.assertTrue(new_root_node.root_node)
        self.assertIn(same_root_node, current_root_node.get_children())

        # Check new node has no FP attempts of its own (already assigned to root)
        fp_attempts = same_root_node.get_fp_attempts()
        expected = {}
        self.assertEqual(fp_attempts, expected)

    def test_add_new_root_node_lower_bound(self):
        """Test adding new root node when same root node exists adds it as child"""
        fp_attempts = self.parsed_fp_attempts[self.test_network_traffic_file]
        new_root_node = RequestNode(1, "https://example.com/script.js",\
                                    fp_attempts.get("https://example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(None, 0, new_root_node, None,\
                                                            fp_attempts, True)

        same_root_node = RequestNode(2, "https://example.com/script.js",\
                                    fp_attempts.get("https://example.com/script.js", {}))
        tree, current_root_node = add_new_root_node(tree, 1, same_root_node, current_root_node,\
                                    fp_attempts, True)

        self.assertEqual(current_root_node, new_root_node)
        self.assertTrue(new_root_node.root_node)

        # If lowerbound, it should not be added twice
        self.assertNotIn(same_root_node, current_root_node.get_children())

    def test_preflight_skipping(self):
        """Test preflight requests are skipped (they are loaded later in a proper event)"""
        resource = {
            "requested_for": "https://www.a.cz/",
            "time": 336436.161914,
            "requested_resource": "https://b.cz/sc.js",
            "initiator": {"type": "preflight"}
        }
        new_node = RequestNode(1, "https://b.cz/sc.js", {})

        assign_direct_parent(resource, self.tree, self.root_node, new_node)
        all_resources = self.tree.get_all_requests()

        # Ensure the preflight resource is not in the tree
        self.assertNotIn("https://b.cz/sc.js", all_resources)

    def test_assign_direct_parent_missing(self):
        """Test that node is added as a child of the curretn root node if parent is unknown"""
        resource = {
            "requested_for": "https://www.a.cz/",
            "time": 336436.161914,
            "requested_resource": "https://b.cz/sc.js",
            "initiator": {"url": "https://c.cz/sc.js", "type": "script"}
        }
        new_node = RequestNode(1, "https://b.cz/sc.js", {})

        assign_direct_parent(resource, self.tree, self.root_node, new_node)
        self.assertIn(new_node, self.root_node.get_children())

    def test_assign_direct_parent(self):
        """Test parent is correctly added when present in the tree already"""
        resource = {
            "requested_for": "https://www.a.cz/",
            "time": 336436.161914,
            "requested_resource": "https://b.cz/sc.js",
            "initiator": {"url": "https://c.cz/sc.js", "type": "script"}
        }
        new_node = RequestNode(1, "https://b.cz/sc.js", {})
        parent_node = RequestNode(1, "https://c.cz/sc.js", {})

        # Add parent node to the tree
        self.root_node.add_child(parent_node)

        assign_direct_parent(resource, self.tree, self.root_node, new_node)

        # Now, check the parent node has a the new node as a child
        self.assertIn(new_node, parent_node.get_children())

    def test_assign_parent_from_callstack(self):
        """Test parent is correctly assigned from stack when it contains at least 1 valid URL"""
        resource = {
            "requested_for": "https://www.a.cz/",
            "time": 336436.161914,
            "requested_resource": "https://a.cz/sc.js",
            "initiator": {
                "stack": {"callFrames": [
                    {"url": "chrome-extension://nn/test"},
                    {"url": "https://b.cz/sc.js"},
                    {"url": ""}]}
            }
        }
        new_node = RequestNode(1, "https://a.cz/sc.js", {})
        parent_node = RequestNode(1, "https://b.cz/sc.js", {})
        self.root_node.add_child(parent_node)

        assign_parent_from_callstack("https://a.cz/sc.js", resource, self.tree,\
                                    self.root_node, new_node)
        self.assertIn(new_node, parent_node.get_children())

    def test_assign_parent_from_callstack_empty(self):
        """Test parent is correctly assigned from callstack when it contains no valid URL"""
        resource = {
            "requested_for": "https://www.a.cz/",
            "time": 336436.161914,
            "requested_resource": "https://a.cz/sc.js",
            "initiator": {
                "stack": {"callFrames": [
                    {"url": "chrome-extension://nn/test"},
                    {"url": ""},
                    {"url": ""}]}
            }
        }
        new_node = RequestNode(1, "https://a.cz/sc.js", {})
        assign_parent_from_callstack("https://a.cz/sc.js", resource, self.tree,\
                                    self.root_node, new_node)
        self.assertIn(new_node, self.root_node.get_children())

    def test_assign_parent_from_callstack_unknown(self):
        """Test root node is assigned as parent when parrent in stack is unknown"""
        resource = {
            "requested_for": "https://www.a.cz/",
            "time": 336436.161914,
            "requested_resource": "https://a.cz/sc.js",
            "initiator": {
                "stack": {"callFrames": [
                    {"url": "chrome-extension://nn/test"},
                    {"url": ""},
                    {"url": "https://unknown-parent.com/js.js"}]}
            }
        }
        new_node = RequestNode(1, "https://a.cz/sc.js", {})
        assign_parent_from_callstack("https://a.cz/sc.js", resource, self.tree,\
                                    self.root_node, new_node)
        self.assertIn(new_node, self.root_node.get_children())

    @patch("source.traffic_parser.create_request_trees.get_traffic_files")
    @patch("source.traffic_parser.create_request_trees.load_json")
    def test_load_network_traffic_files(self, mock_load_json, mock_get_files):
        """Test load_network_traffic_files work as it should"""
        mock_get_files.return_value = [self.test_network_traffic_file]
        mock_load_json.return_value = self.traffic
        result = load_network_traffic_files()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], self.test_network_traffic_file)

    @patch("source.traffic_parser.create_request_trees.load_network_traffic_files")
    def test_create_trees(self, mock_load_files):
        """Test trees are created correctly"""
        mock_load_files.return_value = [(self.traffic, "log_1_network.json")]
        options = MagicMock()
        options.lower_bound_trees = False
        trees = create_trees(self.parsed_fp_attempts, options)
        self.assertIn(self.test_network_traffic_file, trees)

        tree_instance = trees[self.test_network_traffic_file]
        self.assertIsInstance(tree_instance, RequestTree)

        # There should be 8 resources
        # (one loaded 2 times, one assigned to two parents -> presen twice)
        n_of_requests = len(tree_instance.get_all_requests())
        self.assertTrue(n_of_requests == 8)

        # Test FP attempts are correct
        fp_attempts = tree_instance.total_fpd_attempts()
        expected = {"BrowserProperties": 21, "AlgorithmicMethods": 0}
        self.assertEqual(fp_attempts, expected)

    @patch("source.traffic_parser.create_request_trees.load_network_traffic_files")
    def test_create_trees_lower_bound(self, mock_load_files):
        mock_load_files.return_value = [(self.traffic, "log_1_network.json")]
        options = MagicMock()
        options.lower_bound_trees = True
        trees = create_trees(self.parsed_fp_attempts, options)
        self.assertIn(self.test_network_traffic_file, trees)

        tree_instance = trees[self.test_network_traffic_file]
        self.assertIsInstance(tree_instance, RequestTree)

        # There should be 6 resources since no duplicates can exist
        # Check example_network_traffic.json to make ensure (in this folder)
        n_of_requests = len(tree_instance.get_all_requests())
        self.assertTrue(n_of_requests == 6)

        # Test FP attempts are correct
        fp_attempts = tree_instance.total_fpd_attempts()
        expected = {"BrowserProperties": 13, "AlgorithmicMethods": 0}
        self.assertEqual(fp_attempts, expected)
