# test_analysis.py
# Test functions in analysis.py from Analysis Engine
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

from source.analysis_engine.analysis import simulate_blocking, compute_sums_count_resources
from source.analysis_engine.analysis import analyze_trees, compute_averages
from source.analysis_engine.analysis import analyze_tree, parse_partial_results

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.parsed_fp_attempts = \
        {'<anonymous>': {'BrowserProperties': 4, 'AlgorithmicMethods': 0},
            'https://loaded-twice.cz/script.js': {'BrowserProperties': 6, 'AlgorithmicMethods': 0},
            'https://two-parents.cz/script.js': {'BrowserProperties': 2, 'AlgorithmicMethods': 0},
            'https://b.cz/asc.js': {'BrowserProperties': 1, 'AlgorithmicMethods': 0},
            'https://b.cz/sc.js': {'BrowserProperties': 2, 'AlgorithmicMethods': 1},
        }
        self.traffic_file = load_json("./tests/analysis_engine/example_network_traffic.json")
        self.request_tree = reconstruct_tree(self.traffic_file, self.parsed_fp_attempts, False)

    def test_simulate_blocking(self):
        """Test simulate blocking"""
        blocked_resources = ["https://b.cz/sc.js"]
        result = simulate_blocking(self.request_tree, blocked_resources)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["fpd_attempts_observed"],\
                        {'BrowserProperties': 23, 'AlgorithmicMethods': 1})
        self.assertEqual(result["fpd_attempts_blocked_directly"],\
                        {'BrowserProperties': 2, 'AlgorithmicMethods': 1})
        self.assertEqual(result["fpd_attempts_blocked_transitively"],\
                        {'BrowserProperties': 7, 'AlgorithmicMethods': 0})
        self.assertEqual(result["fpd_attempts_blocked_in_total"],\
                        {'BrowserProperties': 9, 'AlgorithmicMethods': 1})
        self.assertEqual(result["requests_observed"], 8)
        self.assertEqual(result["requests_blocked_directly"], 1)
        self.assertEqual(result["requests_blocked_in_total"], 3)
        self.assertEqual(result["requests_blocked_transitively"], 2)
        self.assertEqual(result["requests_blocked_that_have_child_requests"], 1)
        self.assertEqual(result["average_request_block_level"], 3)
        self.assertEqual(result["blocked_subtrees_data"],\
            {"subtrees_fully_blocked": 1, "subtrees_partially_blocked": 0,
            "subtrees_not_blocked": 1, "subtrees_in_total": 2, "trees_with_blocked_root_node": 0})

    def test_compute_sums_count_resources(self):
        """Test compute_sums_count_resources"""

        # Simplified results since compute_sums.. does not care about the number of keys
        results = [{"requests_observed": 3, "average_request_block_level": 0}]
        total_results = {"requests_observed": {"sum": 0, "n_of_results": 0},\
                        "average_request_block_level": {"sum": 0, "n_of_results": 0}}
        updated_results = compute_sums_count_resources(results, total_results)
        self.assertEqual(updated_results["requests_observed"]["sum"], 3)
        self.assertEqual(updated_results["requests_observed"]["n_of_results"], 1)
        self.assertEqual(updated_results["average_request_block_level"]["sum"], 0)
        self.assertEqual(updated_results["average_request_block_level"]["n_of_results"], 0)

    def test_compute_sums_count_resources_fpd(self):
        """Test compute_sums_count_resources with FPD attribute"""

        results = [{"fpd_attempts_observed": {'BrowserProperties': 23, 'AlgorithmicMethods': 1}}]
        total_results = {"fpd_attempts_observed": {"n_of_results": 0, "sum": {}, "average": {}}}

        updated_results = compute_sums_count_resources(results, total_results)
        self.assertEqual(updated_results["fpd_attempts_observed"]["sum"]["BrowserProperties"], 23)
        self.assertEqual(updated_results["fpd_attempts_observed"]["sum"]["AlgorithmicMethods"], 1)
        self.assertEqual(updated_results["fpd_attempts_observed"]["n_of_results"], 1)

    def test_compute_sums_count_resources_subtrees(self):
        """Test compute_sums_count_resources with subtree attribute"""

        results = [{"blocked_subtrees_data": {'subtrees_fully_blocked': 1}}]
        total_results = {"blocked_subtrees_data": {"n_of_results": 0, "sum": {}, "average": {}}}

        updated_results = compute_sums_count_resources(results, total_results)
        self.assertEqual(updated_results["blocked_subtrees_data"]["sum"]\
                        ["subtrees_fully_blocked"], 1)
        self.assertEqual(updated_results["blocked_subtrees_data"]["n_of_results"], 1)


    def test_compute_averages(self):
        """Test compute_averages"""

        total_results = {"requests_observed": {"sum": 3, "n_of_results": 2},\
                        "average_request_block_level": {"sum": 5, "n_of_results": 2}}
        updated_results = compute_averages(total_results)
        self.assertEqual(updated_results["requests_observed"]["average"], 3/2)
        self.assertEqual(updated_results["average_request_block_level"]["average"], 5/2)

    def test_compute_averages_average_block_level(self):
        """Test compute_averages for average block level 0"""

        total_results = {"average_request_block_level": {"sum": 0, "n_of_results": 0}}
        updated_results = compute_averages(total_results)
        self.assertEqual(updated_results["average_request_block_level"]["average"], 0)

    def test_compute_averages_fpd(self):
        """Test compute_averages with FPD attribute"""

        total_results = {"fpd_attempts_observed": {"n_of_results": 2, "sum":
                {'BrowserProperties': 20, 'AlgorithmicMethods': 2}, "average": {}}}

        updated_results = compute_averages(total_results)
        self.assertEqual(updated_results["fpd_attempts_observed"]["average"]\
                        ["BrowserProperties"], 20/2)
        self.assertEqual(updated_results["fpd_attempts_observed"]["average"]\
                         ["AlgorithmicMethods"], 2/2)

    def test_compute_averages_subtrees(self):
        """Test compute_averages with subtree attribute"""

        total_results = {"blocked_subtrees_data": {"n_of_results": 2, "sum":
                        {'subtrees_fully_blocked': 2}, "average": {}}}

        updated_results = compute_averages(total_results)
        self.assertEqual(updated_results["blocked_subtrees_data"]["average"]\
                        ["subtrees_fully_blocked"], 2/2)

    def test_parse_partial_results(self):
        """Test parse partial results"""
        results_1 = {
            "fpd_attempts_observed": {'BrowserProperties': 5},
            "fpd_attempts_blocked_directly": {'BrowserProperties': 1},
            "fpd_attempts_blocked_transitively": {'BrowserProperties': 2},
            "fpd_attempts_blocked_in_total": {'BrowserProperties': 3},
            "requests_observed": 4,
            "requests_blocked_directly": 1,
            "requests_blocked_in_total": 2,
            "requests_blocked_transitively": 1,
            "requests_blocked_that_have_child_requests": 0,
            "average_request_block_level": 3,
            "blocked_subtrees_data": {"subtrees_fully_blocked": 0, "subtrees_partially_blocked": 0,
            "subtrees_not_blocked": 0, "subtrees_in_total": 2, "trees_with_blocked_root_node": 0}
        }

        results_2 = {
            "fpd_attempts_observed": {'BrowserProperties': 1},
            "fpd_attempts_blocked_directly": {'BrowserProperties': 1},
            "fpd_attempts_blocked_transitively": {'BrowserProperties': 0},
            "fpd_attempts_blocked_in_total": {'BrowserProperties': 1},
            "requests_observed": 2,
            "requests_blocked_directly": 1,
            "requests_blocked_in_total": 1,
            "requests_blocked_transitively": 0,
            "requests_blocked_that_have_child_requests": 0,
            "average_request_block_level": 5,
            "blocked_subtrees_data": {"subtrees_fully_blocked": 0, "subtrees_partially_blocked": 0,
            "subtrees_not_blocked": 0, "subtrees_in_total": 1, "trees_with_blocked_root_node": 0}
        }

        results = [results_1, results_2]
        parsed_results = parse_partial_results(results)

        # No need to check them all, only a random few
        self.assertEqual(parsed_results["requests_observed"]["sum"], 6)
        self.assertEqual(parsed_results["requests_observed"]["n_of_results"], 2)
        self.assertEqual(parsed_results["requests_observed"]["average"], 6/2)
        self.assertEqual(parsed_results["fpd_attempts_observed"]["sum"]["BrowserProperties"], 6)

    def test_analyse_tree(self):
        """Test analyse_tree"""
        client_blocked_pages = ["https://b.cz/asc.js"]
        result = analyze_tree(self.request_tree, client_blocked_pages)

        self.assertEqual(result["requests_blocked_directly"], 1)
        self.assertEqual(result["requests_blocked_in_total"], 1)

    def test_analyse_trees(self):
        """Test analyse_trees"""
        request_trees = {"1_network.json": self.request_tree}
        console_output = []

        class ConfigFirefox:
            browser_type = "firefox"

        class ConfigChrome:
            browser_type = "chrome"

        results = analyze_trees(request_trees, console_output, ConfigFirefox())
        results2 = analyze_trees(request_trees, console_output, ConfigChrome())
        self.assertIsInstance(results, dict)
        self.assertIsInstance(results2, dict)

    def test_analyse_trees_exception(self):
        """Test analyse_trees throws an exception when using mismatched browser and logs type"""

        request_trees = {"1_network.json": self.request_tree}

        # Setup chrome logs
        console_output = [{
            "level": "SEVERE",
            "message": "http://test.com - Some Error",
            "source": "network",
            "timestamp": 1
        }]

        # Setup Firefox Config
        class ConfigFirefox:
            browser_type = "firefox"

        # Should throw an error cuz of mismatch
        with self.assertRaises(SystemExit):
            _ = analyze_trees(request_trees, console_output, ConfigFirefox())
