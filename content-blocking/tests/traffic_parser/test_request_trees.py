# test_request_trees.py
# Test the request_trees.py from traffic_parser
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

import unittest
from source.traffic_parser.request_node import RequestNode
from source.traffic_parser.request_tree import RequestTree

class TestRequestTree(unittest.TestCase):
    def setUp(self):
        """Create request tree for testing"""
        self.root = RequestNode("1", "https://example.com/", {})
        self.root.root_node = True

        self.tree = RequestTree(self.root)

        self.root_2 = RequestNode("1", "https://www.example.com/a.html", {})
        self.root_2.root_node = True

        self.child_1 = RequestNode("2", "https://www.example.com/b.js", {"BrowserProperties": 2})
        self.child_2 = RequestNode("3", "https://www.example.com/c.css", {})
        self.child_3 = RequestNode("4", "https://www.example.com/api/d.js",\
                                    {"BrowserProperties": 1})
        self.child_duplicate  = RequestNode("5", "https://www.example.com/api/d.js",\
                                            {"BrowserProperties": 1})

        self.child_of_duplicate = RequestNode("6", "https://www.example.com/dupe.js",\
                                {"BrowserProperties": 2})

        self.root.add_child(self.root_2)
        self.root_2.add_child(self.child_1)
        self.root_2.add_child(self.child_2)
        self.child_1.add_child(self.child_3)
        self.root_2.add_child(self.child_duplicate)

        # Parents are present twice in the tree, add it to both of them
        self.child_duplicate.add_child(self.child_of_duplicate)
        self.child_3.add_child(self.child_of_duplicate)

    def test_get_root(self):
        """Test if get_root returns correct root"""
        self.assertEqual(self.tree.get_root(), self.root)


    def test_total_fpd_attempts(self):
        """Test total FPD attempts"""
        attempts = self.tree.total_fpd_attempts()
        # Even duplicates are calculated at this point,
        # since removing duplicate FP is part of create_request_trees
        self.assertEqual(attempts, {"BrowserProperties": 8})

    def test_first_blocked_fpd_attempts(self):
        """Test first blocked FPD attempts"""
        self.child_1.block()
        self.child_3.block()

        # Only child 1 attempts should count
        attempts = self.tree.first_blocked_fpd_attempts()
        self.assertEqual(attempts, {"BrowserProperties": 2})

    def test_total_blocked_fpd_attempts(self):
        """Test total blocked FPD attempts"""
        self.child_1.block()
        self.child_3.block()

        attempts = self.tree.total_blocked_fpd_attempts()
        self.assertEqual(attempts, {"BrowserProperties": 3})

    def test_total_blocked(self):
        """Test if total blocks are calculated correctly"""
        # Comprehensive transitive blocking is tested in analysis, since the transitive blocking
        # occurs only there - this only test it works manually
        # so 3 blocks (1,3, duplicate)
        self.child_1.block()
        self.assertEqual(self.tree.total_blocked(), 1)
        self.child_2.block()
        self.assertEqual(self.tree.total_blocked(), 2)
        self.child_of_duplicate.block()
        self.assertEqual(self.tree.total_blocked(), 4)

    def test_firstly_blocked(self):
        self.child_1.block()
        self.child_3.block()

        # Only child 1 should be counted
        blocked_nodes = self.tree.firstly_blocked()
        self.assertEqual(blocked_nodes, [self.child_1])

    def test_find_nodes(self):
        """Test node can be found by URL"""
        result = self.tree.find_nodes("https://www.example.com/c.css")
        self.assertEqual(result, [self.child_2])

    def test_doesnt_find_nodes(self):
        """Test node can be found by URL"""
        result = self.tree.find_nodes("https://random.address.com/javascript.js")
        self.assertEqual(result, [])

    def test_find_multiple_nodes(self):
        """Test duplicate nodes are found correctly"""
        result = self.tree.find_nodes("https://www.example.com/api/d.js")
        self.assertEqual(result, [self.child_3, self.child_duplicate])

    def test_get_all_requests(self):
        """Test all requested resources are obtained corretly, including  duplicates"""
        requests = self.tree.get_all_requests()
        # Even though "dupe.js" is only 1 node, it is present as child of two d.js, so exists twice
        expected = [
            "https://example.com/",
            "https://www.example.com/a.html",
            "https://www.example.com/b.js",
            "https://www.example.com/c.css",
            "https://www.example.com/api/d.js",
            "https://www.example.com/api/d.js",
            "https://www.example.com/dupe.js",
            "https://www.example.com/dupe.js"
        ]

        # Check all values are present
        for value in expected:
            self.assertIn(value, requests)

        # Check length matches (duplicates are included)
        self.assertEqual(len(requests), len(expected))

    def test_blocked_at_levels(self):
        """Test block levels are obtained correctly"""
        self.child_1.block()
        self.assertEqual(self.tree.blocked_at_levels(), [3])
        self.child_of_duplicate.block()

        # child_of_duplicate is present twice, but at different levels
        # however, one of the (under child_1) is blocked only transitively, so not counted
        self.assertEqual(self.tree.blocked_at_levels(), [3, 4])

    def test_ascii_tree(self):
        """Test the print_tree function returns a correctly formatted string"""
        output = self.tree.ascii_tree()
        self.assertIn("https://example.com/", output)
        self.assertIn("https://www.example.com/a.html", output)
        self.assertIn("https://www.example.com/b.js", output)
        self.assertIn("https://www.example.com/c.css", output)
        self.assertIn("https://www.example.com/api/d.js", output)
        self.assertIn("https://www.example.com/dupe.js", output)
