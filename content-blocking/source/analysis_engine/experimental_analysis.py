# experimental_analysis.py
# Provides function to compute experimental metrics
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

def get_first_level_with_multiple_children(directly_blocked_tree: RequestTree)\
      -> tuple[str, list[RequestNode], bool]:
    """Function to obtain the first resource in a tree that brings multiple children.
    
    Args:
        directly_blocked_tree: Tree with nodes blocked directly, without transitivity

    Returns:
        tuple:
            - str: Blocking result
            - list[RequestNode]: List of child nodes in the `subtree`
            - bool: Whether a `root block` occured (a root node was blocked)
    """
    current_level = directly_blocked_tree.get_root()

    status = ""
    children = []
    root_block = False

    # If one of the root-level nodes was blocked, mark whole tree as blocked
    if current_level.is_blocked():
        status = "full_block"
        root_block = current_level.root_node

    current_level_children = current_level.get_children()

    # Go down until you either reach a node with 2 or more children or reach a leaf
    while current_level_children:

        # Check if there was >= 2 children
        if len(current_level_children) >= 2:
            children = current_level_children
            break

        # Else go deeper in the tree
        current_level = current_level_children[0]

        if current_level.is_blocked():
            status = "full_block"
            if current_level.root_node:
                root_block = True

        current_level_children = current_level.get_children()

    # If no node with children was found, there was only one tree with no blocks
    if not status:
        status = "no_block"

    return status, children, root_block

def subtree_blocked_status(starting_node: RequestNode) -> str:
    """Function to check if given subtree with root being the starting node
    has either been partially blocked or not blocked at all
    
    Args:
        starting_node: Root node of the subtree
    
    Returns:
        str: Blocking result
    """

    children = starting_node.get_children()

    for child in children:

        # If one of the children was blocked, the tree is partially blocked
        if child.is_blocked():
            return "partial_block"

        # Go recurisvely through the rest of the tree, if a block is found, its also partial block
        result_for_child = subtree_blocked_status(child)
        if result_for_child == "partial_block":
            return "partial_block"

    return "no_block"


def analyse_subtrees_blocking(directly_blocked_tree: RequestTree) -> dict:
    """Function to analyse requested chains inside the request tree. 
    Starting point is first resource with >= 2 children. For each child on this
    level, its own request tree is analysed to calculate fully blocked/partially
    blocked and not blocked at all.

    In case the tree was blocked at the root and the blocked resource has no (or only 1)
    children, the total number of trees is 1.
    
    Args:
        directly_blocked_tree: Tree with nodes blocked directly, without transitivity

    Returns:
        dict: Information about subtree blocking status in the tree
    """

    fully_blocked = 0
    partially_blocked = 0
    not_blocked = 0
    total_trees = 0
    root_blocks = 0

    status, starting_points, root_block = get_first_level_with_multiple_children(\
                                        directly_blocked_tree)

    total_trees = len(starting_points)

    # full block at root level
    if status == "full_block":

        # If there was a root-level block, all subtrees are considered blocked too
        fully_blocked += total_trees
        root_blocks = 1 if root_block else 0

    # no block
    else:

        # Go through all of the subtrees and check if there was some block
        for starting_point in starting_points:

            # Subtree was blocked at the root -> full block and continue
            if starting_point.is_blocked():
                fully_blocked += 1
                continue

            blocked_status = subtree_blocked_status(starting_point)
            if blocked_status == "partial_block":
                partially_blocked += 1
            else:
                not_blocked += 1

    return {
        "subtrees_fully_blocked": fully_blocked, 
        "subtrees_partially_blocked": partially_blocked,
        "subtrees_not_blocked": not_blocked,
        "subtrees_in_total": total_trees,
        "trees_with_blocked_root_node": root_blocks
    }

def add_subtrees(subtrees1: dict, subtrees2: dict) -> dict:
    """Function to add together numbers in subtrees1 and subtrees2
    Used for subtrees blocking analysis
    
    Args:
        subtrees1: Information about subtree analysis in the first tree
        subtrees2: Information about subtree analysis in the second tree

    Returns:
        dict: Joined information about subtree blocking in the two trees
    """

    if subtrees1 == subtrees2 == {}:
        print("Error during subtree analysis! Should never happen!")

    # If one of them is empty (first iteration, nothing saved yet), return the other
    if subtrees1 == {}:
        return subtrees2
    if subtrees2 == {}:
        return subtrees1

    added_dict = {}
    for (key, _) in subtrees1.items():
        first_dict_value = subtrees1[key]
        second_dict_value = subtrees2[key]
        added_dict[key] = first_dict_value + second_dict_value
    return added_dict

def calculate_blocked_who_brings_children(really_blocked_nodes: list[RequestNode])\
      -> int:
    """Function to calculate how many of the directly blocked resources also bring children which
    would be transitively blocked
    
    Args:
        really_blocked_nodes: Nodes that would have been blocked directly by a blocking tool
    
    Returns:
        int: Number of blocked nodes who bring children
    """

    nodes_with_children_blocked = 0
    # Go through each blocked resource
    for node in really_blocked_nodes:

        children = node.get_children()
        # if resource has children, +1
        if children:
            nodes_with_children_blocked += 1

    return nodes_with_children_blocked

def calculate_average_block_level(directly_blocked_tree: RequestTree) -> float:
    """Function to calculate average lbock level in a given tree
    
    Args:
        directly_blocked_tree: Tree with nodes blocked directly, without transitivity

    Returns:
        float: Calculate average block level
    """
    average_block_levels = directly_blocked_tree.blocked_at_levels()
    average_block_level = 0
    if average_block_levels:
        average_block_level = sum(average_block_levels) / len(average_block_levels)
    return average_block_level
