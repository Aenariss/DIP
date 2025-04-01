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
from source.traffic_parser.fp_attempts import obtain_fp_groups, parse_property_logs
from source.traffic_parser.fp_attempts import parse_fp

class TestFPAttempts(unittest.TestCase):
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
    def test_assign_property_group(self, mock_json_load, mock_open):
        """Test property groups are correctly assigned"""
        fp_groups = {"BrowserProperties": "TOP_LEVEL", "NavigatorBasic": "BrowserProperties"}
        wrapped_apis = [{"resource": "Navigator.prototype.languages", \
                         "groups": [{"group": "NavigatorBasic"}]}]
        mock_json_load.return_value = wrapped_apis

        result = assign_property_group(fp_groups)
        self.assertEqual(result, {"Navigator.prototype.languages": ["BrowserProperties"]})

    @patch("builtins.open")
    @patch("json.load")
    def test_assign_property_group_primary(self, mock_json_load, mock_open):
        """Test property groups are correctly assigned for primary parents"""
        fp_groups = {"BrowserProperties": "TOP_LEVEL", "NavigatorBasic": "BrowserProperties"}
        wrapped_apis = [{"resource": "Navigator.prototype.plugins", \
                         "groups": [{"group": "BrowserProperties"}]}]
        mock_json_load.return_value = wrapped_apis

        result = assign_property_group(fp_groups)
        self.assertEqual(result, {"Navigator.prototype.plugins": ["BrowserProperties"]})

    @patch("builtins.open")
    @patch("builtins.exit")
    @patch("json.load")
    def test_assign_property_group_invalid(self, mock_json_load, mock_exit, mock_open):
        """Test property groups returns empty value for unknown primary group 
        should not happen, indicates invalid groups or wrappers file"""
        fp_groups = {"BrowserProperties": "TOP_LEVEL"}
        wrapped_apis = [{"resource": "Navigator.prototype.plugins", \
                         "groups": [{"group": "SomeRandomGroup"}]}]
        mock_json_load.return_value = wrapped_apis

        self.assertRaises(BaseException, assign_property_group(fp_groups))

    @patch("builtins.open")
    @patch("builtins.exit")
    @patch("json.load")
    def test_assign_property_group_two_groups(self, mock_json_load, mock_exit, mock_open):
        """Test property groups has correctly assigned two groups 
        should not happen, indicates invalid groups or wrappers file"""
        fp_groups = {"BrowserProperties": "TOP_LEVEL", "CrawlFpInspector": "TOP_LEVEL"}
        wrapped_apis = [{"resource": "Navigator.prototype.plugins", \
                         "groups": [{"group": "BrowserProperties"}]},
                         {"resource": "Navigator.prototype.plugins", \
                         "groups": [{"group": "CrawlFpInspector"}]}]
        mock_json_load.return_value = wrapped_apis

        result = assign_property_group(fp_groups)
        self.assertEqual(result, {"Navigator.prototype.plugins":\
                                ["BrowserProperties", "CrawlFpInspector"]})

    @patch("builtins.open")
    @patch("json.load")
    def test_obtain_fp_groups(self, mock_json_load, mock_open):
        "Test FP APIs are correctly assigned their primary group"
        groups_data = {"groups": [{"name": "BrowserProperties", \
                                   "groups": [{"name": "NavigatorBasic"}]}]}
        mock_json_load.return_value = groups_data

        result = obtain_fp_groups()
        self.assertEqual(result, {"BrowserProperties": "TOP_LEVEL", "NavigatorBasic": \
                                  "BrowserProperties"})
        
    @patch("builtins.open")
    @patch("json.load")
    def test_obtain_fp_groups_subgroups(self, mock_json_load, mock_open):
        "Test FP APIs are correctly assigned their primary group even recursively"
        groups_data = {"groups": [{"name": "BrowserProperties", \
                                   "groups": [{"name": "NavigatorBasic",
                                               "groups": [{"name": "InsideProperty"}]}]}]}
        mock_json_load.return_value = groups_data

        result = obtain_fp_groups()
        self.assertEqual(result, {"BrowserProperties": "TOP_LEVEL", "NavigatorBasic": \
                                  "BrowserProperties", "InsideProperty": "BrowserProperties"})

    def test_parse_callers_anonymous_end(self):
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

    def test_parse_callers_two_calls_one_page(self):
        """Test parse_callers works as intended when page makes multiple calls"""
        all_callers = {"Error: FPDCallerTracker\n  at https://www.test.org/a/index.js:1:19566\n \
        at eval (eval at <anonymous> (https://www.final.org/b/index.js:1:19566),\
        <anonymous>:3988:11188)": True,\
        "Error: FPDCallerTracker\n  at https://www.test.org/a/index.js:1:19566\n \
        at eval (eval at <anonymous> (https://www.final.org/b/index.js:1:19566),\
        <anonymous>:3988:1117)": True}
        fp_logs = {}
        primary_group = ["BrowserProperties"]
        all_primary_groups = ["BrowserProperties", "AlgorithmicMethods"]
        expected_output = {
            "https://www.final.org/b/index.js": {"BrowserProperties": 2, "AlgorithmicMethods": 0}
        }
        self.assertEqual(parse_callers(all_callers, fp_logs, primary_group, all_primary_groups),\
                        expected_output)

    def test_parse_property_logs_empty_callers(self):
        """Test empty callers are assigned correctly to anonymous"""
        property_logs = {"set":{"args":{"":18},"total":18,"callers":{}}}
        fp_logs = {}
        primary_group = ["BrowserProperties"]
        all_primary_groups = ["BrowserProperties", "AlgorithmicMethods"]
        expected_output = {
            "<anonymous>": {"BrowserProperties": 18, "AlgorithmicMethods": 0}
        }
        fp_logs = parse_property_logs(primary_group, property_logs, fp_logs, all_primary_groups)
        self.assertEqual(expected_output, fp_logs)

    def test_parse_property_logs_empty_callers_twice(self):
        """Test empty callers are assigned correctly to anonymous when called multiple times"""
        property_logs = {"set":{"args":{"":18},"total":18,"callers":{}}}
        fp_logs = {}
        primary_group = ["BrowserProperties"]
        all_primary_groups = ["BrowserProperties", "AlgorithmicMethods"]
        expected_output = {
            "<anonymous>": {"BrowserProperties": 18, "AlgorithmicMethods": 0}
        }
        fp_logs = parse_property_logs(primary_group, property_logs, fp_logs, all_primary_groups)
        self.assertEqual(expected_output, fp_logs)

        property_logs = {"set":{"args":{"":1},"total":1,"callers":{}}}
        expected_output = {
            "<anonymous>": {"BrowserProperties": 19, "AlgorithmicMethods": 0}
        }
        fp_logs = parse_property_logs(primary_group, property_logs, fp_logs, all_primary_groups)
        self.assertEqual(expected_output, fp_logs)

    def test_parse_callers_not_anonymous_end(self):
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

    @patch("builtins.exit")
    def test_get_fp_attempts_invalid_logfile(self, mock_exit):
        """Test the error in get_fp_attempts gets caught"""
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
        all_groups = {}
        property_groups = {"Navigator.prototype.languages": ["BrowserProperties"]}

        # Test exception raised
        self.assertRaises(BaseException, get_fp_attempts(fp_data, all_groups, property_groups))

    def test_get_network_file(self):
        """Test that FP files currently obtain correspoinding network files"""
        self.assertEqual(get_network_file("1_fp.json"), "1_network.json")
        self.assertEqual(get_network_file("2_fp.json"), "2_network.json")

    @patch("builtins.exit")
    def test_get_network_file_invalid(self, mock_exit):
        """Test that invalid files throw an erorr"""
        self.assertRaises(BaseException, get_network_file("1_fp_test.json"))

    @patch("source.traffic_parser.fp_attempts.get_traffic_files")
    @patch("source.traffic_parser.fp_attempts.get_network_file")
    @patch("source.traffic_parser.fp_attempts.load_json")
    @patch("source.traffic_parser.fp_attempts.get_fp_attempts")
    @patch("source.traffic_parser.fp_attempts.assign_property_group")
    @patch("source.traffic_parser.fp_attempts.obtain_fp_groups")
    @patch("source.traffic_parser.fp_attempts.print_progress")
    def test_parse_fp(self, mock_print_progress, mock_obtain_fp_groups,\
        mock_assign_property_group, mock_get_fp_attempts, mock_load_json,\
        mock_get_network_file, mock_get_traffic_files):
        """Test parse_fp can be called and obtains some kind of result"""
        mock_get_traffic_files.return_value = ["1_fp.json"]
        mock_get_network_file.return_value = "1_network.json"

        result = parse_fp()

        # Check key is present in the result dict
        self.assertIn("1_network.json", result,)
