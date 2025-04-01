# requests_analysis.py
# Provides functions for analysis of blocked requests
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
from source.traffic_parser.request_node import RequestNode

def calculate_directly_blocked_requests(directly_blocked_tree: RequestTree) -> int:
    """Function to calculate number of requests blocked directly
    
    Args:
        directly_blocked_tree: Tree with nodes blocked directly, without transitivity

    Returns:
        int: Number of directly blocked requests
    """
    return directly_blocked_tree.total_blocked()

def calculate_total_blocked_requests(transitively_blocked_tree: RequestTree) -> int:
    """Function to calculate number of requests blocked directly and transitively, parents included
    
    Args:
        transitively_blocked_tree: Tree with nodes blocked directly and transitively
    
    Returns:
        int: Number of nodes blocked in total (both directly and transitively)
    """
    return transitively_blocked_tree.total_blocked()

def calculate_really_blocked_requests(directly_blocked_tree: RequestTree) -> list[RequestNode]:
    """Function to calculate how many requests would have been actually blocked
    had the tool been used during the crawl. 
    Calculates the first block nodes in a tree with direct requests alrdy marked as blocked
    Example case:
    A 
    -> B
        -> C
            -> D
    but if B and C would both have been blocked, directly_blocked were 2, but in reality, only 1
    would have been blocked because C and D would not happen
    
    Args:
        directly_blocked_tree: Tree with nodes blocked directly, without transitivity

    Returns:
        list[RequestNode]: list of nodes that would have been blocked on real page
    """
    return directly_blocked_tree.firstly_blocked()
