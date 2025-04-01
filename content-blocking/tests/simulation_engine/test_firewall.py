# test_firewall.py
# Test the functions used in firewall.py from simulation_engine
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
from source.simulation_engine.firewall import setup_block_rule, remove_block_rule
from source.simulation_engine.firewall import firewall_block_traffic, firewall_unblock_traffic

class TestFirewall(unittest.TestCase):

    def test_setup_block_rule(self):
        """Test that setup_block_rule generates the correct firewall command"""
        expected_command = 'netsh advfirewall firewall add rule name="Test" \
dir=out action=block protocol=TCP remoteport=443'
        self.assertEqual(setup_block_rule("Test", "TCP", "443"), expected_command)

    def test_remove_block_rule(self):
        """Test that remove_block_rule generates the correct firewall command"""
        expected_command = 'netsh advfirewall firewall delete rule name="Test"'
        self.assertEqual(remove_block_rule("Test"), expected_command)

    @patch("source.simulation_engine.firewall.os.system")
    def test_firewall_block_traffic(self, mock_os_system):
        """Test firewall_block_traffic correctly calls os.system twice"""
        firewall_block_traffic()
        self.assertEqual(mock_os_system.call_count, 2)

    @patch("source.simulation_engine.firewall.os.system")
    def test_firewall_unblock_traffic(self, mock_os_system):
        """Test firewall_unblock_traffic correctly calls os.system twice"""
        firewall_unblock_traffic()
        self.assertEqual(mock_os_system.call_count, 2)
