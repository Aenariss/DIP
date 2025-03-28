# firewall.py
# Controls Windows firewall to block outgoing HTTP(S) communication. Requires admin privileges.
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

# built-in modules
import os

BLOCK_HTTP_RULE_NAME = "Block-HTTP"
BLOCK_HTTPS_RULE_NAME = "Block-HTTPS"

def setup_block_rule(name: str, protocol: str, port: str) -> str:
    """Function to setup command to add rule using netsh utility
    Needs name of the rule, protocol to use and port to block"""

    netsh_str = f"netsh advfirewall firewall add rule name=\"{name}\" dir=out action=block "
    netsh_str += f"protocol={protocol} remoteport={port}"

    return netsh_str

def remove_block_rule(name: str) -> str:
    """Function to setup command to remove firewall rule using netsh"""

    netsh_str = f"netsh advfirewall firewall delete rule name=\"{name}\""

    return netsh_str

def firewall_block_traffic() -> None:
    """Method to block outgoing communication on ports 80 and 443 using windows firewall"""
    block_port_80 = setup_block_rule(BLOCK_HTTP_RULE_NAME, "TCP", 80)
    block_port_443 = setup_block_rule(BLOCK_HTTPS_RULE_NAME, "TCP", 443)

    print("Setting up custom Firewall rules...")
    os.system(block_port_80)
    os.system(block_port_443)

def firewall_unblock_traffic() -> None:
    """Method to unblock outgoing communication on ports 80 and 443 using windows firewall"""
    unblock_port_80 = remove_block_rule(BLOCK_HTTP_RULE_NAME)
    unblock_port_443 = remove_block_rule(BLOCK_HTTPS_RULE_NAME)

    print("Removing custom Firewall rules...")
    os.system(unblock_port_80)
    os.system(unblock_port_443)
