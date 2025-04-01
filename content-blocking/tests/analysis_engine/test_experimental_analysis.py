# test_experimental_analysis.py
# Test functions in experimental_analysis.py from Analysis Engine
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

# Custom modules
from source.file_manipulation import load_json
from source.traffic_parser.create_request_trees import reconstruct_tree
from source.traffic_parser.request_node import RequestNode

from source.analysis_engine.analysis_utils import get_directly_blocked_tree
from source.analysis_engine.requests_analysis import calculate_really_blocked_requests
from source.analysis_engine.experimental_analysis import calculate_average_block_level
from source.analysis_engine.experimental_analysis import calculate_blocked_who_brings_children
from source.analysis_engine.experimental_analysis import add_subtrees
from source.analysis_engine.experimental_analysis import analyse_subtrees_blocking
from source.analysis_engine.experimental_analysis import subtree_blocked_status
from source.analysis_engine.experimental_analysis import get_first_level_with_multiple_children


class TestExperimentalAnalysis(unittest.TestCase):
    def setUp(self):
        self.traffic_file = load_json("./tests/analysis_engine/example_network_traffic.json")
        self.request_tree = reconstruct_tree(self.traffic_file, {}, False)

        # Add new node for testing
        b_asc = self.request_tree.find_nodes("https://b.cz/asc.js")
        new_node = RequestNode("1", "https://b.cz/dasc.js", {})
        b_asc[0].add_child(new_node)


    def test_get_first_level_with_multiple_children(self):
        """Test finding first level with multiple children"""
        blocked_resources = ["https://b.cz/sc.js", "https://loaded-twice.cz/script.js"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        # b.cz/sc.js and loaded-twice.cz/script.js are the roots of subtrees
        # no blocking at root level, so status is no_block and root_block is false
        self.assertEqual(status, "no_block")
        self.assertEqual(len(children), 2)
        self.assertFalse(root_block)

    def test_get_first_level_with_multiple_children_root_block(self):
        """Test finding first level with multiple children"""
        blocked_resources = ["https://a.cz/", "https://www.a.cz/"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        # two root nodes are blocked, so full block and root block
        self.assertEqual(status, "full_block")
        self.assertEqual(len(children), 2)
        self.assertTrue(root_block)

    def test_subtree_blocked_status_no_block(self):
        """Test subtree analysis where nothing is blocked"""
        blocked_resources = []
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        self.assertEqual(status, "no_block")
        self.assertEqual(len(children), 2)
        self.assertFalse(root_block)
        self.assertEqual(subtree_blocked_status(children[0]), "no_block")

    def test_subtree_blocked_status_partial_block(self):
        """Test subtree analysis with partial block"""
        blocked_resources = ["https://b.cz/asc.js"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        self.assertEqual(status, "no_block")
        self.assertEqual(len(children), 2)
        self.assertFalse(root_block)
        self.assertEqual(subtree_blocked_status(children[0]), "partial_block")

    def test_subtree_blocked_status_partial_block_recursive(self):
        """Test subtree analysis with partial block recursively"""
        blocked_resources = ["https://b.cz/dasc.js"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        self.assertEqual(status, "no_block")
        self.assertEqual(len(children), 2)
        self.assertFalse(root_block)
        self.assertEqual(subtree_blocked_status(children[0]), "partial_block")

    def test_analyse_subtrees_blocking_full_block(self):
        """Test subtree blocking with full_block"""
        blocked_resources = ["https://a.cz/"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        result = analyse_subtrees_blocking(directly_blocked_tree)
        self.assertEqual(result["subtrees_fully_blocked"], len(children))
        self.assertEqual(result["subtrees_partially_blocked"], 0)
        self.assertEqual(result["subtrees_not_blocked"], 0)
        self.assertEqual(result["subtrees_in_total"], len(children))
        self.assertEqual(result["trees_with_blocked_root_node"], 1)

    def test_analyse_subtrees_blocking_subtree_root_and_partial(self):
        """Test subtree blocking with full_block at subtree root level and partial block in another
        """
        blocked_resources = ["https://b.cz/dasc.js", "https://loaded-twice.cz/script.js"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        result = analyse_subtrees_blocking(directly_blocked_tree)
        self.assertEqual(result["subtrees_fully_blocked"], 1)
        self.assertEqual(result["subtrees_partially_blocked"], 1)
        self.assertEqual(result["subtrees_not_blocked"], 0)
        self.assertEqual(result["subtrees_in_total"], len(children))
        self.assertEqual(result["trees_with_blocked_root_node"], 0)

    def test_analyse_subtrees_blocking_subtree_no_block(self):
        """Test subtree analysis with no blocking"""
        blocked_resources = []
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        status, children, root_block = get_first_level_with_multiple_children(directly_blocked_tree)

        result = analyse_subtrees_blocking(directly_blocked_tree)
        self.assertEqual(result["subtrees_fully_blocked"], 0)
        self.assertEqual(result["subtrees_partially_blocked"], 0)
        self.assertEqual(result["subtrees_not_blocked"], 2)
        self.assertEqual(result["subtrees_in_total"], len(children))
        self.assertEqual(result["trees_with_blocked_root_node"], 0)

    def test_add_subtrees(self):
        """Test adding subtree analysis results"""
        results_1 = {"subtrees_fully_blocked": 2, "subtrees_partially_blocked": 1}
        results_2 = {"subtrees_fully_blocked": 1, "subtrees_partially_blocked": 2}
        result = add_subtrees(results_1, results_2)
        self.assertEqual(result["subtrees_fully_blocked"], 3)
        self.assertEqual(result["subtrees_partially_blocked"], 3)

    def test_add_subtrees_first_empty(self):
        """Test adding subtree analysis results when first subtree is empty"""
        results_1 = {}
        results_2 = {"subtrees_fully_blocked": 1, "subtrees_partially_blocked": 2}
        result = add_subtrees(results_1, results_2)
        self.assertEqual(result["subtrees_fully_blocked"], 1)
        self.assertEqual(result["subtrees_partially_blocked"], 2)

    def test_add_subtrees_second_empty(self):
        """Test adding subtree analysis results when second subtree is empty"""
        results_1 = {"subtrees_fully_blocked": 2, "subtrees_partially_blocked": 1}
        results_2 = {}
        result = add_subtrees(results_1, results_2)
        self.assertEqual(result["subtrees_fully_blocked"], 2)
        self.assertEqual(result["subtrees_partially_blocked"], 1)

    def test_add_subtrees_both_empty(self):
        """Test adding subtree analysis results when both are empty"""
        results_1 = {}
        results_2 = {}
        result = add_subtrees(results_1, results_2)
        self.assertEqual(result, {})

    def test_calculate_blocked_who_brings_children(self):
        """Test counting nodes that have blocked children"""
        blocked_resources = ["https://b.cz/dasc.js", "https://b.cz/asc.js"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        really_blocked_nodes = calculate_really_blocked_requests(directly_blocked_tree)

        result = calculate_blocked_who_brings_children(really_blocked_nodes)
        self.assertEqual(len(really_blocked_nodes), 1)
        self.assertEqual(result, 1)

    def test_calculate_average_block_level(self):
        """Test calculation of average block level"""
        blocked_resources = ["https://b.cz/asc.js"]
        directly_blocked_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)

        average_blocks = calculate_average_block_level(directly_blocked_tree)
        self.assertEqual(average_blocks, 4)
