# analysis.py
# The analysis engine where request trees are used to perform analysis.
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
import re

# custom modules
from source.request_tree import RequestTree, RequestNode, add_substract_fp_attempts
from source.utils import print_progress, squash_tree_resources
from source.constants import BROWSER_TYPE

def get_first_level_with_multiple_children(request_tree: RequestTree)\
      -> tuple[str, list[RequestNode], bool]:
    """Function to obtain the first resource in a tree that brings multiple children."""
    current_level = request_tree.get_root()

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
            root_block = current_level.root_node

        current_level_children = current_level.get_children()

    # If no node with children was found, there was only one tree with no blocks
    if not status:
        status = "no_block"

    return status, children, root_block

def subtree_blocked_status(starting_node: RequestNode) -> str:
    """Function to check if given subtree with root being the starting node
    has either been partially blocked or not blocked at all"""

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


def analyse_subtrees_blocking(request_tree: RequestTree) -> dict:
    """Function to analyse requested chains inside the request tree. 
    Starting point is first resource with >= 2 children. For each child on this
    level, its own request tree is analysed to calculate fully blocked/partially
    blocked and not blocked at all.

    In case the tree was blocked at the root and the blocked resource has no (or only 1)
    children, the total number of trees is 1.
    
    :param request_tree: Tree with directly blocked resources"""

    fully_blocked = 0
    partially_blocked = 0
    not_blocked = 0
    total_trees = 0
    root_blocks = 0

    status, starting_points, root_block = get_first_level_with_multiple_children(request_tree)

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
        "trees_blocked_because_root_node": root_blocks
    }

def add_subtrees(subtrees1: dict, subtrees2: dict) -> dict:
    """Function to add together numbers in subtrees1 and subtrees2
    Used for subtrees blocking analysis"""

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

def calculate_directly_blocked(request_tree: RequestTree, blocked_resources: list[str])\
     -> tuple[RequestTree, int]:
    """Function to calculate number of requests blocked directly"""
    # block only parent nodes to obtain how many would be observed without request chain
    for resource in blocked_resources:
        nodes_with_resource = request_tree.find_nodes(resource)
        for node in nodes_with_resource:

            # Mark initial node as blocked
            node.block()

    # Obtain number of blocked requests in the tree with no recursive blocking
    blocked_directly = request_tree.total_blocked()
    return request_tree, blocked_directly

def calculate_transitively_blocked(request_tree: RequestTree, blocked_resources: list[str])\
     -> tuple[RequestTree, int]:
    """Function to calculate number of requests blocked directly and transitively, parents included
    
    request_tree already needs to have direct parents blocked"""
    # Go through each blocked resource and check if its present in the tree
    for resource in blocked_resources:
        nodes_with_resource = request_tree.find_nodes(resource)
        for parent_node in nodes_with_resource:

            # Mark initial node as blocked
            parent_node.block()

            # Also mark all children as blocked
            child_nodes = parent_node.get_all_children_nodes()

            for node in child_nodes:
                node.block()

    # Go through the whole tree and calculate numer of blocked
    total_blocked = request_tree.total_blocked()
    return request_tree, total_blocked

def calculate_really_blocked(request_tree: RequestTree) -> list[RequestNode]:
    """Function to calculate how many requests would have been actually blocked
    had the tool been used during the crawl. 
    Calculates the first block nodes in a tree with direct requests alrdy marked as blocked
    Example case:
    A 
    -> B
        -> C
            -> D
    but if B and C would both have been blocked, blocked_directly returns 2, but in reality, only 1
    would have been blocked because C and D would not happen"""

    really_blocked_nodes = request_tree.firstly_blocked()
    return really_blocked_nodes

def calculate_blocked_who_brings_children(really_blocked_nodes: list[RequestNode])\
      -> int:
    """Function to calculate how many of the directly blocked resources also bring children which
    would be transitively blocked"""

    nodes_with_children_blocked = 0
    # Go through each blocked resource
    for node in really_blocked_nodes:

        children = node.get_children()
        # if resource has children, +1
        if children:
            nodes_with_children_blocked += 1

    return nodes_with_children_blocked


def simulate_blocking(request_tree: RequestTree, blocked_resources: list[str]) -> dict:
    """Defines and computes various data about each page with simulated content-blocking
    tool present. Assumes the requested resources would have been the same with the 
    content-blockin tool present.
    """

    # Get number of total resources
    total_requested = len(request_tree.get_all_requests())
    total_fpd_attempts = request_tree.total_fpd_attempts()

    # First, calculate direct parent blocks
    directly_blocked_tree, _ = calculate_directly_blocked(request_tree,\
                                                            blocked_resources)

    # Second, block all child nodes transitively if parent is blocked
    transitively_blocked_tree, total_blocked = calculate_transitively_blocked(\
        directly_blocked_tree, blocked_resources)

    really_blocked_nodes = calculate_really_blocked(directly_blocked_tree)
    directly_blocked = len(really_blocked_nodes)
    blocked_transitively = total_blocked - directly_blocked

    blocked_subtrees_data = analyse_subtrees_blocking(directly_blocked_tree)

    direct_fpd_blocked = directly_blocked_tree.first_blocked_fpd_attempts()
    total_fpd_blocked = transitively_blocked_tree.total_blocked_fpd_attempts()
    transitive_fpd_blocked = add_substract_fp_attempts(total_fpd_blocked, direct_fpd_blocked,\
                                                        add=False)

    average_block_levels = directly_blocked_tree.blocked_at_levels()
    average_block_level = 0 # Default value if no blocked requests
    if average_block_levels:
        average_block_level = sum(average_block_levels) / len(average_block_levels)
    blocked_with_children = calculate_blocked_who_brings_children(really_blocked_nodes)

    return {
        # Total FPD attempts observed
        "fpd_attempts_observed": total_fpd_attempts,
        # Number of FPD attempts blocked directly
        "fpd_attempts_blocked_directly": direct_fpd_blocked,
        # Number of FPD attempts blocked transitively
        "fpd_attempts_blocked_transitively": transitive_fpd_blocked,
        # Total number of FPD attempts blocked
        "fpd_attempts_blocked_in_total": total_fpd_blocked,
        # Number of all rsources requested
        "requests_observed": total_requested,
        # Number of resources blocked directly
        "requests_blocked_directly": directly_blocked,
        # Number of all resources blocked (even transtiviely)
        "requests_blocked_in_total": total_blocked,
        # Number of resources blocked transitively
        "requests_blocked_transitively": blocked_transitively,
        # N of blocked resources which brought kids
        "requests_blocked_that_have_child_requests": blocked_with_children,
        # Average level at which resource was blocked
        "average_request_block_level": average_block_level,
        # N of fully/partially/not blocked subtrees
        "blocked_subtrees_data": blocked_subtrees_data
    }

def parse_console_logs_chrome(console_output: list[dict]) -> list[str]:
    """Function to parse obtained console logs from Chrome"""
    blocked_by_client_error = "ERR_BLOCKED_BY_CLIENT"
    blocked_by_administrator_error = "ERR_BLOCKED_BY_ADMINISTRATOR"
    error_length = len(blocked_by_client_error)
    error_length_2 = len(blocked_by_administrator_error)

    blocked_pages = []

    for report in console_output:
        # Only do anything if it was an error
        if report["level"] == "SEVERE":
            message = report["message"]

            # Obtain the last part of the string w/ the error
            try:
                last_part = message[-error_length:]
                last_part_2 = message[-error_length_2:]

                # It was blocked by client
                if last_part == blocked_by_client_error or\
                   last_part_2 == blocked_by_administrator_error:

                    # get the url of the resource - split by space and the first is url
                    parts_of_message = message.split(' ')
                    url = parts_of_message[0]
                    blocked_pages.append(url)

            # If obtaining was impossible, it was not an error
            except Exception:
                continue

    return blocked_pages

def parse_partial_results(results: list[dict]) -> dict:
    """Calculates finished results from a collection of partial results by
    computing the sum and/or average of each value"""

    sub_result = {
        "n_of_results": 0,
        "sum": 0,
        "average": 0
    }

    sub_result_dicts = {
        "n_of_results": 0,
        "sum": {},
        "average": {}
    }

    # Initialize completed results, needs to use same keys as in simulate_blocking() function
    total_results = {
        "fpd_attempts_observed": dict(sub_result_dicts),
        "fpd_attempts_blocked_directly": dict(sub_result_dicts),
        "fpd_attempts_blocked_transitively": dict(sub_result_dicts),
        "fpd_attempts_blocked_in_total": dict(sub_result_dicts),
        "requests_observed": dict(sub_result),
        "requests_blocked_directly": dict(sub_result),
        "requests_blocked_in_total": dict(sub_result),
        "requests_blocked_transitively": dict(sub_result),
        "requests_blocked_that_have_child_requests": dict(sub_result),
        "average_request_block_level": dict(sub_result),
        "blocked_subtrees_data": dict(sub_result_dicts)
    }

    # Go through all partial results
    for result in results:

        # For each result, go through each sub-result
        for (sub_result, total_result) in total_results.items():

            # Update total_results accordingly
            total_result["n_of_results"] += 1

            # Check if its not fpd - we need to be special for that
            if "fpd" in sub_result:
                total_result["sum"] = add_substract_fp_attempts(total_result["sum"],\
                                                                result[sub_result])
            # Subtrees are special case since they use dicts but are not FPD
            elif sub_result == "blocked_subtrees_data":
                total_result["sum"] = add_subtrees(total_result["sum"], result[sub_result])
            else:
                total_result["sum"] += result[sub_result]

    # Now each result has sum value stored in together with nubmer of results - calculate averages
    for (sub_result, total_result) in total_results.items():

        # If its FPD stat, I need to approach it by calculating each FP sub-attribute
        if "fpd" in sub_result or sub_result == "blocked_subtrees_data":

            # Create deep copy of sum to divide by n_of_results
            total_result["average"] = dict(total_result["sum"])
            for (group_name, count) in total_result["average"].items():
                total_result["average"][group_name] = count / total_result["n_of_results"]

        else:
            total_result["average"] = total_result["sum"] / total_result["n_of_results"]

    return total_results

def process_firefox_console_output(request_trees: dict, console_output: list) -> list:
    """Function to substract logged resources from all observed resources
    to fix different output types since FF logs all CORRECT resources"""
    all_resources = squash_tree_resources(request_trees)
    correct_resources = console_output

    dict_correct_resources = {}

    # Make correct resources into dict to provide efficiency for later substraction (hashtable ftw)
    for resource in correct_resources:
        dict_correct_resources[resource] = True

    # Automatically populate correct resources with blob: and data:. Blobs always
    # return an error since I'm not loading them locally and data: are not network
    # resources -> they can't be blocked.
    # Also skip internal data such as those starting with about:, chrome-extension://...
    for resource in all_resources:
        add_to_correct = False
        if resource.startswith("blob:"):
            add_to_correct = True

        elif resource.startswith("data:"):
            add_to_correct = True

        elif resource.startswith("about:"):
            add_to_correct = True

        elif resource.startswith("chrome:"):
            add_to_correct = True

        elif re.match(r"chrome-(.*)\/\/", resource):
            add_to_correct = True

        if add_to_correct:
            dict_correct_resources[resource] = True

    # If resource was NOT in correctly logged resources, it is BLOCKED
    blocked_resources = [resource for resource in all_resources\
                        if dict_correct_resources.get(resource, None) is None]

    return blocked_resources

def analyse_tree(request_tree: RequestTree, console_output: list, options: dict) -> dict:
    """Function to calculate how many requests in a tree would be blocked 
    if given resources were blocked and how many fp attempts that would prevent"""

    # Get list of blocked pages depending on whether they came from Chrome or FF

    client_blocked_pages = None
    if options.get(BROWSER_TYPE) == "chrome":
        # Obtain URLs of resources that were blocked by client
        client_blocked_pages = parse_console_logs_chrome(console_output)
    else:
        client_blocked_pages = console_output

    # Calculate what would have happened hat the content blocking tool been present
    results = simulate_blocking(request_tree, client_blocked_pages)

    return results

def analyse_trees(request_trees: dict, console_output: list, options: dict) -> list:
    """Function to launch analysis on each tree and calculate average values 
    of each observed property"""

    # If current experiment was done on firefox, console output contains all passed resources
    # So what we need to do is remove those logged from all logged => rest is blocked
    if options.get(BROWSER_TYPE) == "firefox":
        console_output = process_firefox_console_output(request_trees, console_output)

    # Analyse each tree
    progress_printer = print_progress(len(request_trees), "Analysing blocked pages...")
    all_results = []

    for (_, tree) in request_trees.items():
        progress_printer()
        analysis_results = analyse_tree(tree, console_output, options)
        all_results.append(analysis_results)

    all_results = parse_partial_results(all_results)

    return all_results
