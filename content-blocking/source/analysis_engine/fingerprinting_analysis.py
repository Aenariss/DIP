# fingerprinting_analysis.py
# Provides functions for analysis of anti-tracking performance
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

# Custom modules
from source.traffic_parser.request_tree import RequestTree

def calculate_directly_blocked_fpd_attempts(directly_blocked_tree: RequestTree) -> dict:
    """Function to calculate FPD attempts blocked directly.
    
    Args:
        directly_blocked_tree: Tree with nodes blocked directly, without transitivity
    
    Returns:
        dict: Information about FPD attempts blocked directly in the tree
    """
    return directly_blocked_tree.first_blocked_fpd_attempts()

def calculate_total_blocked_fpd_attempts(transitively_blocked_tree: RequestTree) -> dict:
    """Function to calculate FPD attempts blocked both directly and transitively.
    
    Args:
        transitively_blocked_tree: Tree with nodes blocked directly and transitively
    
    Returns:
        dict: Information about total FPD attempts blocked in the tree
    """
    return transitively_blocked_tree.total_blocked_fpd_attempts()

def calculate_total_fpd_attempts(request_tree: RequestTree) -> dict:
    """Function to calculate total FPD attempts in the tree.
    
    Args:
        request_tree: Tree with FPD attempts assigned to nodes
    
    Returns:
        dict: Information about total number of FPD attempts observed in the tree
    """
    return request_tree.total_fpd_attempts()
