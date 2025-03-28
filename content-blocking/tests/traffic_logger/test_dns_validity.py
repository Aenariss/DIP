# test_dns_validity.py
# Test the is_dns_valid from traffic_logger.py
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
from source.traffic_logger.traffic_loader import is_dns_valid, get_address

class TestIsDnsValid(unittest.TestCase):

    def test_get_address(self):
        """Test if get_address work as it should"""

        url = "https://www.example.com/script_with_long_name.js"
        domain = get_address(url)

        self.assertEqual(domain, "www.example.com")

    def test_get_address_fail(self):
        """Test if get_address fails when invalid domain"""

        url = "localhost:8000/"
        domain = get_address(url)

        self.assertEqual(domain, "")

        url = "https://missing-final-slash.com"
        domain = get_address(url)

        self.assertEqual(domain, "")

    def test_valid_dns_logs(self):
        """Test that all network resources have corresponding DNS logs."""

        dns_traffic = {
            "example.com": {
                "www": {"A": ["192.168.1.1"], "CNAME": []}
            },
            "first-level.cz": {
                "first-level.cz": {"A": ["192.168.1.2"], "CNAME": []}
            }
        }
        network_traffic = [{"requested_resource": "https://www.example.com/a.js"},
                           {"requested_resource": "https://first-level.cz/"}]

        valid, clean_dns_traffic = is_dns_valid(dns_traffic, network_traffic)

        self.assertTrue(valid)

        # nothing should be removed in this case
        self.assertEqual(dns_traffic, clean_dns_traffic)

    def test_missing_dns_logs(self):
        """Test if missing network logs are detected"""

        dns_traffic = {
            "example.com": {
                "www": {"A": ["192.168.1.1"], "CNAME": []}
            }
        }
        network_traffic = [
            {"requested_resource": "https://www.example.com/page"},
            {"requested_resource": "https://missing.example.com/resource"}
        ]

        valid, cleaned_dns = is_dns_valid(dns_traffic, network_traffic)

        # Check it failed since missing.example.com is not present in DNS logs
        self.assertFalse(valid)
        self.assertEqual(cleaned_dns, {})  # Should return empty dict due to missing DNS

    def test_unnecessary_dns_entries_removed(self):
        """Test if unnecessary DNS logs are removed if they dont match any network"""
        dns_traffic = {
            "example.com": {
                "www": {"A": ["192.168.1.1"], "CNAME": []},
            },
            "unused.com": {
                "www": {"A": ["10.10.10.10"], "CNAME": []}
            }
        }
        network_traffic = [{"requested_resource": "https://www.example.com/"}]

        valid, cleaned_dns = is_dns_valid(dns_traffic, network_traffic)

        self.assertTrue(valid)
        self.assertNotIn("unused", cleaned_dns)

    def test_cname_records(self):
        """Test that CNAME records are correctly present in cleand DNS logs"""
        dns_traffic = {
            "example.com": {
                "www": {
                    "A": ["192.168.1.1"], "CNAME": ["alias.example.com"]
                },
                "alias.example.com": {
                    "A": [], "CNAME": ["example.cname.com"]
                }
            },
            "cname.com": {
                "example": {
                    "A": ["192.168.1.1"], "CNAME": []
                }
            }
        }
        network_traffic = [{"requested_resource": "https://www.example.com/"}]

        valid, cleaned_dns = is_dns_valid(dns_traffic, network_traffic)

        self.assertTrue(valid)
        self.assertIn("cname.com", cleaned_dns)
        self.assertIn("example.com", cleaned_dns)
