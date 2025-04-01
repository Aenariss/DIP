# test_request_nodes.py
# Test the request_nodes.py from traffic_parser
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

class TestRequestNode(unittest.TestCase):
    def setUp(self):
        """Create nodes to be used in tests"""
        self.node_1 = RequestNode("1", "https://example.com/a.js", {})
        self.node_2 = RequestNode("2", "https://example.com/b.js", {})
        self.node_3 = RequestNode("3", "https://example.com/c.js", {})
        self.node_duplicated = RequestNode("4", "https://example.com/c.js", {})

    def test_add_child(self):
        """Test adding a child adds it into the child array of the parent and vice-versa"""
        self.node_1.add_child(self.node_2)
        self.assertIn(self.node_2, self.node_1.get_children())
        self.assertIn(self.node_1, self.node_2.get_parents())

    def test_add_parent(self):
        """Test adding a parent adds the Node into its parent array and vice-versa"""
        self.node_2.add_parent(self.node_1)
        self.assertIn(self.node_1, self.node_2.get_parents())
        self.assertIn(self.node_2, self.node_1.get_children())

    def test_add_duplicate_child(self):
        """Test adding Node with the same resource twice doesnt actually add it twice"""
        self.node_1.add_child(self.node_3)
        self.node_1.add_child(self.node_duplicated)
        self.assertEqual(len(self.node_1.get_children()), 1)

    def test_add_duplicate_parent(self):
        """Test adding the same parent twice doesnt actually add it"""
        self.node_2.add_parent(self.node_3)
        self.node_2.add_parent(self.node_3)
        self.assertEqual(len(self.node_2.get_parents()), 1)

    def test_adding_default_children(self):
        """Test children nodes specified are added as children"""
        node_4 = RequestNode("8", "https://example.com/d.js", {}, children=[self.node_3])
        self.assertIn(self.node_3, node_4.get_children())

    def test_blocking_non_repeated_node(self):
        """Test if a node can be blocked"""
        self.node_1.block()
        self.assertTrue(self.node_1.is_blocked())

    def test_blocking_repeated_node(self):
        """Test if a node cannot be blocked when using "repeated" lower-bound settings"""
        self.node_1.repeated = True
        self.node_1.block()
        self.assertFalse(self.node_1.is_blocked())

    def test_blocking_multiple_parents_node(self):
        """Test if a node cannot be blocked when using "transitive_block" if it has
        non-blocked parent"""
        self.node_1.add_parent(self.node_2)
        self.node_1.add_parent(self.node_3)

        self.node_2.block()
        self.node_1.block(transitive_block=True)
        self.assertFalse(self.node_1.is_blocked())

    def test_blocking_multiple_parents_node_both(self):
        """Test if a node is blocked when using "transitive_block" if it has
        all parents blocked"""
        self.node_1.add_parent(self.node_2)
        self.node_1.add_parent(self.node_3)

        self.node_2.block()
        self.node_3.block()
        self.node_1.block(transitive_block=True)
        self.assertTrue(self.node_1.is_blocked())

    def test_get_all_children_resources(self):
        """Test get_all_children_resources works transitively as it should"""
        self.node_1.add_child(self.node_2)
        self.node_2.add_child(self.node_3)
        self.node_1.add_child(self.node_duplicated)
        children_resources = self.node_1.get_all_children_resources()
        expected_resources = ["https://example.com/a.js", "https://example.com/b.js",\
                              "https://example.com/c.js", "https://example.com/c.js"]

        # Check length matches and check all expected are present
        self.assertEqual(len(expected_resources), len(children_resources))
        for resource in expected_resources:
            self.assertIn(resource, children_resources)

    def test_get_all_children_nodes(self):
        """Test get_all_children_nodes works transitively as it should"""
        self.node_1.add_child(self.node_2)
        self.node_2.add_child(self.node_3)
        self.node_1.add_child(self.node_duplicated)
        children_nodes = self.node_1.get_all_children_nodes()
        expected_nodes = [self.node_1, self.node_2, self.node_3, self.node_duplicated]

        # Check length matches and check all expected are present
        self.assertEqual(len(expected_nodes), len(children_nodes))
        for node in expected_nodes:
            self.assertIn(node, expected_nodes)
