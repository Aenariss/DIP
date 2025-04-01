# request_tree.py
# The class representing a request_tree.
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

from source.traffic_parser.request_node import RequestNode
from source.utils import add_substract_fp_attempts

class RequestTree:
    """Class representing the whole tree-like request chain
    
    Args:
        root_node: Node representing the root of the tree
    """
    def __init__(self, root_node: RequestNode) -> None:
        """Initialization method
        
        Args:
            root_node: Node representing root of this tree
        """
        self.root_node = root_node

    def get_root(self) -> RequestNode:
        """Method to retunr the root of the tree (initial page URL)
        
        Returns:
            RequestNode: Root of this tree
        """
        return self.root_node

    def total_fpd_attempts(self, start: RequestNode=None) -> dict:
        """Method to calculate total number of FP attempts observed in a tree
        
        Args:
            start: Node from which to start counting FP attempts in this tree
        
        Returns:
            dict: Total number of FP attempts associated with Nodes in the tree
        """
        if start is None:
            start = self.get_root()

        fpd_attempts = {}

        # Get fpd attempts of starting node
        fpd_attempts = add_substract_fp_attempts(start.get_fp_attempts(), fpd_attempts)

        # Repeat for all children
        for child in start.get_children():
            fpd_attempts = add_substract_fp_attempts(
                self.total_fpd_attempts(start=child), fpd_attempts)

        return fpd_attempts

    def first_blocked_fpd_attempts(self, start: RequestNode=None) -> dict:
        """Method to calculate number of FP attempts stopeed at first blocked parent.
        Can be used to calculate FP attempts blocked directly since it does not count 
        transitively.
        
        Args:
            start: Node from which to start calculating directly blocked FP attempts
        
        Returns:
            dict: Total number of directly blocked FP attempts
        """
        if start is None:
            start = self.get_root()

        blocked_attempts = {}

        # If starting node is blocked, return it as an array
        if start.is_blocked():
            blocked_attempts = start.get_fp_attempts()
            return blocked_attempts

        # If start was not blocked, repeat for all children
        for child in start.get_children():
            blocked_attempts = add_substract_fp_attempts(
                self.first_blocked_fpd_attempts(start=child), blocked_attempts)

        return blocked_attempts

    def total_blocked_fpd_attempts(self, start: RequestNode=None) -> dict:
        """Method to calculate total number of FPD attempts blockedd in a tree.
        Assumes all required nodes throught the tree have been blocked.
        
        Args:
            start: Node from which to start calculating total blocked FPD attempts

        Returns:
            dict: Total number of directly+transitively blocked FP attempts
        """
        if start is None:
            start = self.get_root()

        blocked_attempts = {}

        # If starting node is blocked, return it as an array
        if start.is_blocked():
            blocked_attempts = add_substract_fp_attempts(start.get_fp_attempts(), blocked_attempts)

        # Repeat for all children
        for child in start.get_children():
            blocked_attempts = add_substract_fp_attempts(
                self.total_blocked_fpd_attempts(start=child), blocked_attempts)

        return blocked_attempts

    def blocked_at_levels(self, start: RequestNode=None, level: int=1) -> list[int]:
        """Method to return levels at which first block in chain was observed
        e.g. if in tree A->B->[C,D], E->F; C and F was blocked, returns [3,4]
        
        Args:
            start: Node from which to start counting
            level: Level this node is located at
        
        Returns:
            list: List of levels a blocked node was first encountered at
        """
        if start is None:
            start = self.get_root()

        blocked = []

        # If starting node is blocked, return it as an array
        if start.is_blocked():
            blocked.append(level)
            return blocked

        # If start was not blocked, repeat for all children
        for child in start.get_children():
            blocked_at_level = self.blocked_at_levels(start=child, level=level+1)
            blocked.extend(blocked_at_level)

        return blocked

    def firstly_blocked(self, start: RequestNode=None) -> list[RequestNode]:
        """Method to compute how many of resources would have been blocked in 
        reality by counting only the first in a tree blocked. Returns list of such
        resources
        
        Args:
            start: Node from which to start computing
        
        Returns:
            list: Blocked nodes (without their children)
        """
        if start is None:
            start = self.get_root()

        blocked = []

        # If starting node is blocked, return it as an array
        if start.is_blocked():
            blocked.append(start)
            return blocked

        # If start was not blocked, repeat for all children
        for child in start.get_children():
            blocked.extend(self.firstly_blocked(start=child))
        return blocked

    def total_blocked(self, start: RequestNode=None) -> int:
        """Method to compute the total number of blocked resources in a tree
        
        Args:
            start: Node from which to start computing

        Returns:
            int: Total number of blocked nodes in this tree
        """
        if start is None:
            start = self.get_root()

        blocked = 0

        # Check if the initial node is blocked
        if start.is_blocked():
            blocked += 1

        # For each child calculate how many of its children are blocked
        for child in start.get_children():
            blocked = blocked + self.total_blocked(start=child)

        return blocked

    def get_all_requests(self, start_node: RequestNode=None) -> list[str]:
        """Method to recursively get all resources requested on a page
        
        Args:
            start_node: Node from which to start obtaining resources

        Returns:
            list: All resources in the tree
        """
        if not start_node:
            start_node = self.get_root()

        requests_with_root_as_start = start_node.get_all_children_resources()

        return requests_with_root_as_start

    def _recursive_node_check(self, node: RequestNode, searched_resource: str)\
        -> list[RequestNode]:
        """Internal method to recursively check if a resource URL is present in the tree
        
        Args:
            node: Node from which to start checking if searched resource is present in the tree
            searched_resource: URL of the searched resource

        Returns:
            list: All nodes of which URL matches the searched resource
        """

        results = []

        # The node is what we're searching for - return it immediatly, resource\
        # can't have itself as a child
        if node.get_resource() == searched_resource:
            return [node]

        # Else recursively continue with children and return all matches
        for child_node in node.get_children():
            result = self._recursive_node_check(child_node, searched_resource)
            if result:
                results.extend(result)
        return results

    def find_nodes(self, searched_resource: str) -> list[RequestNode]:
        """Method to check if a resource is present in the tree and return nodes that contain it
        
        Args:
            searched_resource: URL of the resource searched in the tree
        
        Returns:
            list: List of Nodes containing the searched resource
        """
        return self._recursive_node_check(self.get_root(), searched_resource)

    def ascii_tree(self, level: int=1, current_node: RequestNode=None) -> str:
        """Method to return a CLI-visual of the requests in a given tree
        
        Args:
            level: How deep the printed node should be
            current_node: Node to print
            printing: If output should go to stdout
        Returns:
            str: The tree visualization as a string
        """

        # Print the initial request - tree root
        result = ""

        if not current_node:
            current_node = self.get_root()

        current_fp_attempts = str(current_node.get_fp_attempts())
        block_result = "-- Blocked" if current_node.is_blocked() else "-- Loaded"

        # Add current level to result
        result += '\n|' + '--' * 2 * level + ' ' + current_node.get_resource()[:100] + ' '\
                + block_result + ' ' + current_fp_attempts

        # Recursively print for children
        for child in current_node.get_children():
            result += self.ascii_tree(level=level+1, current_node=child)

        return result
