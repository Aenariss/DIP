# test_fp_attempts.py
# Test the fp_attempts.py from traffic_parser
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
from source.traffic_parser.fp_attempts import get_primary_groups, construct_default_fp_value
from source.traffic_parser.fp_attempts import parse_callers, get_fp_attempts
from source.traffic_parser.fp_attempts import get_network_file, assign_property_group
from source.traffic_parser.fp_attempts import obtain_fp_groups

class TestFingerprintingParser(unittest.TestCase):
    def test_get_primary_groups(self):
        """Test primary groups are correctly obtained"""
        all_groups = {
            "BrowserProperties": "TOP_LEVEL",
            "NavigatorBasic": "BrowserProperties",
            "AlgorithmicMethods": "TOP_LEVEL",
            "JSFontEnum": "FontsEnumFingerprint"
        }
        expected_output = ["BrowserProperties", "AlgorithmicMethods"]
        self.assertEqual(get_primary_groups(all_groups), expected_output)

    def test_construct_default_fp_value(self):
        """Test default FP attempts of primary groups are correctly constructed"""
        primary_groups = ["BrowserProperties", "AlgorithmicMethods"]
        expected_output = {"BrowserProperties": 0, "AlgorithmicMethods": 0}
        self.assertEqual(construct_default_fp_value(primary_groups), expected_output)

    @patch("builtins.open")
    @patch("json.load")
    def test_assign_property_group(self, mock_json_load, _):
        """Test property groups are correctly assigned"""
        fp_groups = {"BrowserProperties": "TOP_LEVEL", "NavigatorBasic": "BrowserProperties"}
        wrapped_apis = [{"resource": "Navigator.prototype.languages", \
                         "groups": [{"group": "NavigatorBasic"}]}]
        mock_json_load.return_value = wrapped_apis

        result = assign_property_group(fp_groups)
        self.assertEqual(result, {"Navigator.prototype.languages": ["BrowserProperties"]})

    @patch("builtins.open")
    @patch("json.load")
    def test_obtain_fp_groups(self, mock_json_load, _):
        "TEst FP APIs are correctly assigned their primary group"
        groups_data = {"groups": [{"name": "BrowserProperties", \
                                   "groups": [{"name": "NavigatorBasic"}]}]}
        mock_json_load.return_value = groups_data

        result = obtain_fp_groups()
        self.assertEqual(result, {"BrowserProperties": "TOP_LEVEL", "NavigatorBasic": \
                                  "BrowserProperties"})

    def test_parse_callers(self):
        """Test parse_callers works as intended"""
        all_callers = {"Error: FPDCallerTracker\n  at https://www.test.org/a/index.js:1:19566\n \
        at eval (eval at <anonymous> (https://www.final.org/b/index.js:1:19566),\
        <anonymous>:3988:11188)": True}
        fp_logs = {}
        primary_group = ["BrowserProperties"]
        all_primary_groups = ["BrowserProperties", "AlgorithmicMethods"]
        expected_output = {
            "https://www.final.org/b/index.js": {"BrowserProperties": 1, "AlgorithmicMethods": 0}
        }
        self.assertEqual(parse_callers(all_callers, fp_logs, primary_group, all_primary_groups),\
                        expected_output)

        all_callers = {"Error: FPDCallerTracker\n    at Navigator.replacementPD \
        (chrome-extension://a:970:11)\n    at Object.apply (chrome-extension://a:405:25)\n \
        at https://b.com/script.js:57:697\n    at https://c.cz/script.js:330:440": True}
        fp_logs = {}
        primary_group = ["BrowserProperties"]
        all_primary_groups = ["BrowserProperties", "AlgorithmicMethods"]
        expected_output = {
            "https://c.cz/script.js": {"BrowserProperties": 1, "AlgorithmicMethods": 0}
        }
        self.assertEqual(parse_callers(all_callers, fp_logs, primary_group, all_primary_groups),\
                        expected_output)

    def test_get_fp_attempts(self):
        """Test the main get_fp_attempts works as intended"""
        fp_data = \
        {"fpd_access_logs": {
                "440647870": {
                    "Navigator.prototype.languages": 
                    {"get":{"args":{"":129},"total":129,"callers": \
                    {"Error: FPDCallerTracker\n  at https://www.test.org/a/index.js:1:19566\n at \
                     eval (eval at <anonymous> (https://www.final.org/b/index.js:1:19566), \
                     <anonymous>:3988:11188)": True}}}
                }
            }
        }
        all_groups = {"NavigatorBasic": "BrowserProperties", "BrowserProperties": "TOP_LEVEL"}
        property_groups = {"Navigator.prototype.languages": ["BrowserProperties"]}
        fp_attempts = get_fp_attempts(fp_data, all_groups, property_groups)
        self.assertEqual(fp_attempts, {"https://www.final.org/b/index.js":\
                                    {"BrowserProperties": 1}})

    def test_get_network_file(self):
        """Test that FP files currently obtain correspoinding network files"""
        self.assertEqual(get_network_file("1_fp.json"), "1_network.json")
        self.assertEqual(get_network_file("2_fp.json"), "2_network.json")
