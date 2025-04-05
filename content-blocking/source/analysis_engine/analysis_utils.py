# analysis_utils.py
# Utils to be used during analysis
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

# Custom modules
from source.traffic_parser.request_tree import RequestTree
from source.utils import squash_tree_resources

def get_directly_blocked_tree(request_tree: RequestTree, blocked_resources: list[str])\
    -> RequestTree:
    """Function to obtain request tree with simulation results projected into it
    Only blocks the nodes which were blocked during the simulation
    
    Args:
        request_tree: Original request tree of requests on a page
        blocked_resources: list of all blocked resources
    
    Returns:
        RequestTree: Tree with blocked nodes (those matching blocked_resources)
    """
    # Block only parent nodes to obtain how many would be observed without request chain
    for resource in blocked_resources:
        nodes_with_resource = request_tree.find_nodes(resource)
        for node in nodes_with_resource:

            # Mark initial node as blocked
            node.block()

    return request_tree

def get_transitively_blocked_tree(request_tree: RequestTree, blocked_resources: list[str])\
    -> RequestTree:
    """Function to obtain request tree with simulation results projected into it
    Takes into account transitive properties of the request tree
    
    Args:
        request_tree: Original request tree of requests on a page
        blocked_resources: list of all blocked resources
    
    Returns:
        RequestTree: Tree with transitively blocked nodes (if parent was blocked, so was child)
    """
    # Go through each blocked resource and check if its present in the tree
    for resource in blocked_resources:
        nodes_with_resource = request_tree.find_nodes(resource)
        for parent_node in nodes_with_resource:

            # Mark initial node as blocked
            parent_node.block()

            # Also mark all children as blocked
            child_nodes = parent_node.get_all_children_nodes()

            # If parent was repeated (lowerbound calculation), mark all children as repeated
            if parent_node.repeated:
                for node in child_nodes:
                    node.repeated = True

            # Try to block all child nodes transitively
            for node in child_nodes:
                node.block(transitive_block=True)

    return request_tree

def parse_console_logs_chrome(console_output: list[dict]) -> list[str]:
    """Function to parse obtained console logs from Chrome
    
    Args:
        console_output: Console output logged from Chrome simulation

    Returns:
        list[str]: List of blocked resources
    """
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
            last_part = message[-error_length:]
            last_part_2 = message[-error_length_2:]

            # It was blocked by client
            if last_part == blocked_by_client_error or\
                last_part_2 == blocked_by_administrator_error:

                # get the url of the resource - split by space and the first is url
                parts_of_message = message.split(' ')
                url = parts_of_message[0]
                blocked_pages.append(url)

    return blocked_pages

def process_firefox_console_output(request_trees: dict, console_output: list) -> list:
    """Function to substract logged resources from all observed resources
    to fix different output types since FF logs all CORRECT resources
    
    Args:
        request_trees: Request trees for all processed pages
        console_output: Logged requests from firefox browser

    Returns:
        list: List of resources blocked by a given Firefox-based tool
    """
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
                        if not dict_correct_resources.get(resource, False)]

    return blocked_resources
