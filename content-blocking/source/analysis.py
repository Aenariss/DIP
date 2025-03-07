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

# custom modules
from source.request_tree import RequestTree, RequestNode, add_substract_fp_attempts
from source.utils import print_progress

def get_first_level_with_multiple_children(request_tree: RequestTree) -> list[RequestNode] | str:
    """Function to obtain the first resource in a tree that brings multiple children."""
    current_level = request_tree.get_root()

    # If one of the root-level nodes was blocked, mark whole tree as blocked
    if current_level.is_blocked():
        return "full_block"

    current_level_children = current_level.get_children()

    # Go down until you either reach a node with 2 or more children or reach a leaf
    while current_level_children:

        # CCheck if there was >= 2 children
        if len(current_level_children) >= 2:
            return current_level_children

        # Else go deeper in the tree
        current_level = current_level_children[0]

        if current_level.is_blocked():
            return "partial_block"

        current_level_children = current_level.get_children()

    # If no node with children was found, there was only one tree with no blocks
    return "no_block"

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

    starting_points = get_first_level_with_multiple_children(request_tree)

    # Obtained actual starting point
    if isinstance(starting_points, list):
        total_trees = len(starting_points)

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

    # There was some kind of blocking (or none at all) in the root tree
    # So only 1 tree in total was observed
    else:
        total_trees = 1
        if starting_points == "full_block":
            fully_blocked += 1
        elif starting_points == "partial_block":
            partially_blocked += 1
        elif starting_points == "no_block":
            not_blocked += 1

    return {
        "fully_blocked": fully_blocked, 
        "partially_blocked": partially_blocked,
        "not_blocked": not_blocked,
        "total_trees": total_trees
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
        "total_fpd_attempts": total_fpd_attempts, # Total FPD attempts observed
        "direct_fpd_blocked": direct_fpd_blocked, # Number of FPD attempts blocked directly
        "total_fpd_blocked": total_fpd_blocked, # Total number of FPD attempts blocked
        "transitive_fpd_blocked": transitive_fpd_blocked, # Number of FPD attempts blocked tran.
        "directly_blocked": directly_blocked, # Number of resources blocked directly
        "total_requested": total_requested, # Number of all rsources requested
        "total_blocked": total_blocked, # Number of all resources blocked (even transtiviely)
        "blocked_transitively": blocked_transitively, # Number of resources blocked transitively
        "blocked_with_children": blocked_with_children, # N of blocked resources which brought kids
        "average_block_level": average_block_level, # Average level at which resource was blocked
        "blocked_subtrees_data": blocked_subtrees_data # N of fully/partially/not blocked subtrees
    }

def get_unresolved(console_output: list[dict]) -> list[str]:
    unresolved_error = "ERR_NAME_NOT_RESOLVED"
    sock_error = "ERR_SOCKET_NOT_CONNECTED"
    unresolved_length = len(unresolved_error)
    sock_length = len(sock_error)
    unresolved_pages = []

    for report in console_output:
        # Only do anything if it was an error
        if report["level"] == "SEVERE":
            message = report["message"]

            # Obtain the last part of the string w/ the error
            try:
                last_part = message[-unresolved_length:]
                last_part_2 = message[-sock_length:]

                # It was blocked by client
                if last_part == unresolved_error or last_part_2 == sock_error:

                    # get the url of the resource - split by space and the first is url
                    parts_of_message = message.split(' ')
                    url = parts_of_message[0]
                    unresolved_pages.append(url)

            # If obtaining was impossible, it was not an error
            except Exception:
                continue

    return unresolved_pages

def filter_out_unresolved(request_trees: dict, unresolved_requests: list, printer: callable)\
    -> dict:
    """Function to filter out trees containing unresolved results"""
    okay_trees = {}
    for (key, tree) in request_trees.items():
        printer()
        nodes_with_resource = tree.get_all_requests()
        okay_trees[key] = tree
        for unresolved in unresolved_requests:
            if unresolved in nodes_with_resource:
                del okay_trees[key]
                break
    return okay_trees

def parse_console_logs(console_output: list[dict]) -> list[str]:
    """Function to parse obtained console logs"""
    # Works for chrome - check it works for firefox!
    blocked_by_client_error = "ERR_BLOCKED_BY_CLIENT"
    error_length = len(blocked_by_client_error)

    blocked_pages = []

    for report in console_output:
        # Only do anything if it was an error
        if report["level"] == "SEVERE":
            message = report["message"]

            # Obtain the last part of the string w/ the error
            try:
                last_part = message[-error_length:]

                # It was blocked by client
                if last_part == blocked_by_client_error:

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
    computing the sum and/or average of each value
    
    "total_fpd_attempts": Total FPD attempts observed across all pages (SUM, AVG)
    "direct_fpd_blocked": Number of FPD attempts blocked directly (SUM, AVG)
    "total_fpd_blocked": Total number of FPD attempts blocked across all pages (SUM, AVG)
    "transitive_fpd_blocked": Number of FPD attempts blocked transitively (SUM, AVG)
    "directly_blocked": Number of resources blocked directly (SUM, AVG)
    "total_requested": Number of all rsources requested (SUM, AVG)
    "total_blocked": Number of all resources blocked (even transtiviely) (SUM, AVG)
    "blocked_transitively": Number of resources blocked transitively (SUM, AVG)
    "blocked_with_children": N of blocked resources which brought kids (SUM, AVG)
    "average_block_level": Average level at which resource was blocked (AVG)
    "blocked_subtrees_data": N of subtrees fully/partially/not blocked (AVG, SUM)
    """

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
        "total_fpd_attempts": dict(sub_result_dicts),
        "direct_fpd_blocked": dict(sub_result_dicts),
        "total_fpd_blocked": dict(sub_result_dicts),
        "transitive_fpd_blocked": dict(sub_result_dicts),
        "directly_blocked": dict(sub_result),
        "total_requested": dict(sub_result),
        "total_blocked": dict(sub_result),
        "blocked_transitively": dict(sub_result),
        "blocked_with_children": dict(sub_result),
        "average_block_level": dict(sub_result),
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

def analyse_tree(request_tree: RequestTree, console_output: list[dict]) -> dict:
    """Function to calculate how many requests in a tree would be blocked 
    if given resources were blocked and how many fp attempts that would prevent"""

    # Obtain URLs of resources that were blocked by client
    client_blocked_pages = parse_console_logs(console_output)

    # Calculate what would have happened hat the content blocking tool been present
    results = simulate_blocking(request_tree, client_blocked_pages)

    return results

def analyse_trees(request_trees: dict, console_output: list[dict]) -> list:
    """Function to launch analysis on each tree and calculate average values 
    of each observed property"""

    # Filter out trees with incomplete DNS records Selenium might have screwed up
    unresolved_requests = get_unresolved(console_output)
    progress_printer = print_progress(len(request_trees), "Removing trees with unresolved DNS...")
    request_trees = filter_out_unresolved(request_trees, unresolved_requests, progress_printer)

    # Analyse each tree
    progress_printer = print_progress(len(request_trees), "Analysing blocked pages...")
    all_results = []

    for (_, tree) in request_trees.items():
        progress_printer()
        analysis_results = analyse_tree(tree, console_output)
        all_results.append(analysis_results)

    all_results = parse_partial_results(all_results)

    return all_results
