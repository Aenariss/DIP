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
from source.request_tree import RequestTree, RequestNode
from source.utils import print_progress

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
    - > B
        - > C
            - > D)
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
    tool present.
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

    direct_fpd_blocked = directly_blocked_tree.first_blocked_fpd_attempts()
    total_fpd_blocked = transitively_blocked_tree.total_blocked_fpd_attempts()
    transitive_fpd_blocked = total_fpd_blocked - direct_fpd_blocked

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
        "average_block_level": average_block_level # Average level at which resource was blocked
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
    """

    sub_result = {
        "n_of_results": 0,
        "sum": 0,
        "average": 0
    }

    # Initialize completed results, needs to use same keys as in simulate_blocking() function
    total_results = {
        "total_fpd_attempts": dict(sub_result),
        "direct_fpd_blocked": dict(sub_result),
        "total_fpd_blocked": dict(sub_result),
        "transitive_fpd_blocked": dict(sub_result),
        "directly_blocked": dict(sub_result),
        "total_requested": dict(sub_result),
        "total_blocked": dict(sub_result),
        "blocked_transitively": dict(sub_result),
        "blocked_with_children": dict(sub_result),
        "average_block_level": dict(sub_result) 
    }

    # Go through all partial results
    for result in results:

        # For each result, go through each sub-result
        for (sub_result, total_result) in total_results.items():

            # Update total_results accordingly
            total_result["n_of_results"] += 1
            total_result["sum"] += result[sub_result]

    # Now each result has sum value stored in together with nubmer of results - calculate averages
    for (_, total_result) in total_results.items():
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
