# test_fingerprinting_analysis.py
# Test functions in fingerprinting_analysis.py from Analysis Engine
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

from source.analysis_engine.analysis_utils import get_directly_blocked_tree
from source.analysis_engine.analysis_utils import get_transitively_blocked_tree
from source.analysis_engine.fingerprinting_analysis import calculate_directly_blocked_fpd_attempts
from source.analysis_engine.fingerprinting_analysis import calculate_total_blocked_fpd_attempts
from source.analysis_engine.fingerprinting_analysis import calculate_total_fpd_attempts

class TestFingerprintingAnalysis(unittest.TestCase):
    def setUp(self):
        self.parsed_fp_attempts = \
        {'<anonymous>': {'BrowserProperties': 4, 'AlgorithmicMethods': 0},
            'https://loaded-twice.cz/script.js': {'BrowserProperties': 6, 'AlgorithmicMethods': 0},
            'https://two-parents.cz/script.js': {'BrowserProperties': 2, 'AlgorithmicMethods': 0},
            'https://b.cz/asc.js': {'BrowserProperties': 1, 'AlgorithmicMethods': 0},
            'https://example.com/script.js': {'BrowserProperties': 1, 'AlgorithmicMethods': 0},
        }
        self.traffic_file = load_json("./tests/analysis_engine/example_network_traffic.json")
        self.request_tree = reconstruct_tree(self.traffic_file, self.parsed_fp_attempts, False)

    def test_calculate_directly_blocked_fpd_attempts(self):
        """Test calculate_directly blocked works as it should"""
        blocked_resources = ["https://b.cz/asc.js"]
        direct_tree = get_directly_blocked_tree(self.request_tree, blocked_resources)
        directly_blocked = calculate_directly_blocked_fpd_attempts(direct_tree)
        self.assertEqual({"BrowserProperties": 1, "AlgorithmicMethods": 0}, directly_blocked)

    def test_calculate_total_blocked_fpd_attempts(self):
        """Test total block calculation works"""
        # Mock the total_blocked method for transitive tree
        blocked_resources = ["https://b.cz/sc.js"]
        total_block_tree = get_transitively_blocked_tree(self.request_tree, blocked_resources)
        total_blocked = calculate_total_blocked_fpd_attempts(total_block_tree)

        # sc.js has two children -> loaded-twice and asc.js, and loaded-twice has two-parents
        # but two-parents was loaded also by a.cz, so it cant be blocked, so only sc, asc
        # and loaded-twice
        self.assertEqual({"BrowserProperties": 7, "AlgorithmicMethods": 0}, total_blocked)

    def test_calculate_total_fpd_attempts(self):
        """Test total obsserved work as it should"""

        all_fp_attempts = calculate_total_fpd_attempts(self.request_tree)
        self.assertEqual({"BrowserProperties": 21, "AlgorithmicMethods": 0}, all_fp_attempts)
