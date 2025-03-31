# crate_request_trees.py
# Recreate the request tree based on the observed HTTP traffic.
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
import os
import sys

# Custom modules
from source.file_manipulation import load_json, get_traffic_files
from source.utils import print_progress, add_substract_fp_attempts
from source.config import Config
from source.traffic_parser.request_node import RequestNode
from source.traffic_parser.request_tree import RequestTree

ANONYMOUS_CALLERS = "<anonymous>"


def fix_missing_parent(current_root_node: RequestNode, resource_node: RequestNode) -> None:
    """handle initiator when child resource was loaded before the parent, should rarely happen
    
    Args:
        current_root_node: Node representing the current root node
        resource_node: Node to be added as a child of the current root node
    """

    # If parent was not found, it might be because of some javascript-magic or because of iframes
    # that open for about:srcdoc or something like that. In that case, I'm unable to tell.
    # So just add it as parent of the root resource
    current_root_node.add_child(resource_node)

def join_call_frames(stack: dict) -> list[str]:
    """Function to recursively obtain the callstack containing all parents
    
    Args:
        stack: initator call stack attribute
    Returns:
        list: URLs of callers in the call stack, the final caller is the last
    """
    frames = []

    # Recursively obtain all parents if they exist
    # Go from the bottom -> Deepest parent first
    parent = stack.get("parent")
    if parent:
        deeper_parents = join_call_frames(parent)
        frames.extend(deeper_parents)

    # Add results from the current callframe
    # Reverse the list because the first in the stack is the final which caused it
    # -> should be last
    current_callframe = stack.get("callFrames", [])[::-1]
    for call in current_callframe:
        frames.append(call["url"])

    return frames

def add_new_root_node(tree: RequestTree, resource_counter: int, node: RequestNode,\
                current_root_node: RequestNode, fp_attempts: dict, lower_bound_trees: bool)\
                -> tuple[RequestTree, RequestNode]:
    """Function to replace current root node with new root node or create a tree if
    it's the very first primary request
    
    Args:
        tree: RequestTree that is being edited
        resource_counter: How many network events have been parsed
        node: New potential Root Node
        current_root_node: Current Root Node
        fp_attempts: FP attempts associated with a resource
        lower_bound_trees: If we are creating lower_bound_trees

    Returns:
        tuple:
            - RequestTree: the updated current tree
            - RequestNode: Root Node to be used as Current Root Node
    """

    # Get anonymous attempts
    anonymous_attempts = fp_attempts.get(ANONYMOUS_CALLERS, {})
    if resource_counter == 0:
        tree = RequestTree(node)

        node.root_node = True

        # Add anonymous attempts to the root
        # Get number of attempts already associated with root
        root_fp_attempts = node.get_fp_attempts()

        # Combine the root FP attempts with anonymous caller FP attempts
        new_total = add_substract_fp_attempts(root_fp_attempts, anonymous_attempts)
        node.set_fp_attempts(new_total)

    else:
        # Check if the request is not to a page already in the tree ->
        # It is unnecessary for the analysis and makes results weird.
        # Just add it as a regular child of the previous global level
        if tree.find_nodes(node.get_resource()):

            if lower_bound_trees:
                # Do not repeat root nodes if lower bound
                return tree, current_root_node

            current_root_node.add_child(node)

            # Remove FP attempts that are associated with this node, since it is a duplicate
            # They are already associated with the main node
            node.set_fp_attempts({})

            return tree, current_root_node

        current_root_node.add_child(node)
        node.root_node = True

        # Delete all anonymous FP attempts from the previous root node and add them to the new one
        root_fp_attempts = current_root_node.get_fp_attempts()
        previous_root_node_fp_attempts = add_substract_fp_attempts(root_fp_attempts,\
                                                         anonymous_attempts, add=False)
        current_root_node.set_fp_attempts(previous_root_node_fp_attempts)

        new_root_node_fp_attempts = node.get_fp_attempts()
        with_anonymous_callers = add_substract_fp_attempts(new_root_node_fp_attempts,\
                                                           anonymous_attempts)

        node.set_fp_attempts(with_anonymous_callers)

    current_root_node = node
    return tree, current_root_node

def assign_direct_parent(resource: dict, tree: RequestTree, current_root_node: RequestNode,\
        node: RequestNode) -> None:
    """Function to assign parent if present as initator.url
    
    Args:
        resource: currently parsed network event
        tree: Current Request Tree
        current_root_node: The current root node
        node: The node to be assigned as a child to the parent
    """

    # Skip preflights since they will be loaded later anyway
    if resource["initiator"]["type"] == "preflight":
        return

    # Check if the parent is already present
    parent_nodes = tree.find_nodes(resource["initiator"]["url"])

    # Parent not known should not happen often (child resource loaded before parent)
    if not parent_nodes:
        # If it was not preflight, it's strange, so handle it
        fix_missing_parent(current_root_node, node)

    # Parent present, add it as their child
    else:
        # Resource can be requested by multiple requests -> add some printing here if analysing
        if len(parent_nodes) > 1:
            pass

        # Problem - how do I know which parent is the correct one?
        # A was requested 7 times by different resources. A requested B. Which from the
        # 7 A is responsible? Assign to all.
        for parent_node in parent_nodes:
            parent_node.add_child(node)

def assign_parent_from_callstack(current_resource: str, resource: dict, tree: RequestTree,\
        current_root_node: RequestNode, node: RequestNode) -> None:
    """Function to assign parents from initiator call stack
    
    Args:
        current_resource: URL of the currently parsed resource
        resource: currently parsed network event
        tree: Current Request Tree
        current_root_node: The current root node
        node: The node to be assigned as a child to the parent
    """

    # Concatenate all call stacks
    calls = join_call_frames(resource["initiator"]["stack"])

    # Add the loaded resource to the end
    calls.append(current_resource)

    # Remove dynamic content with no known initiator
    # and chrome-extension JShelter wrappers
    # "" -> B -> C = just B -> C
    calls = [x for x in calls if (x != '') and not x.startswith("chrome-extension")]

    # Obtain only the direct initiator - only look for the final request that
    # caused the resource to be loaded.
    last_two_calls = calls[-2:]

    if len(last_two_calls) == 2:

        # Check if the parent is already known (should be)
        parent_nodes = tree.find_nodes(last_two_calls[0])

        for parent_node in parent_nodes:
            parent_node.add_child(node)

        # If parent unknown, try to fix it (should not happen)
        if parent_nodes == []:
            fix_missing_parent(current_root_node, node)

    # If all callframes were empty (dynamic), just set the last
    # global level as parent of the resource
    if len(calls) == 1:
        current_root_node.add_child(node)


def reconstruct_tree(observed_traffic: dict, fp_attempts: dict, lower_bound_trees: bool)\
      -> RequestTree:
    """Function to reconstruct initiator chains from observed traffic and assign FP
    attempts to each page
    
    Args:
        observed_traffic: The logged network traffic
        fp_attempts: Possibly FP API calls observed during network logging
        lower_bound_trees: Whether to create lower_bound_trees (no duplicate nodes)

    Returns:
        RequestTree: Class representing the created tree which contains the request structure
    """
    tree = None
    requests_count = len(observed_traffic)
    current_root_node = None

    for resource_number in range(requests_count):
        resource = observed_traffic[resource_number]
        current_resource = resource["requested_resource"]
        # If time is unavailable, use maximum
        time = resource.get("time", sys.maxsize)

        # Either get number of observed FP attempts or 0 if none observed
        resource_fp_attempts = fp_attempts.get(current_resource, {})

        # Create new Node object representing the resource. Creates duplicit requests!!
        node = RequestNode(time, current_resource, fp_attempts=resource_fp_attempts, children=[])

        # If requested_for matches requested_resource and initiator type is "other"
        # it's a new root node, parse it accordingly
        if resource["requested_for"] == current_resource and\
            resource["initiator"]["type"] == "other":

            # Also, no URL attribute can be present
            if resource["initiator"].get("url", {}) == {}:
                tree, current_root_node = add_new_root_node(tree, resource_number,\
                                        node, current_root_node, fp_attempts, lower_bound_trees)

        else:
            # Do not repeat FP attempts for nodes already in the tree -> the original node
            # already has them all
            existing_nodes = tree.find_nodes(current_resource)
            if existing_nodes:
                node.set_fp_attempts({})

            # Solve LOWER-BOUND issue of A -> B,C -> A,C by limiting at msot one of all.
            if lower_bound_trees:
                if existing_nodes:
                    node = existing_nodes[0]
                    node.repeated = True

                    # Need to continue here because adding parents for lower bound breaks the logic
                    # since A -> B -> A would make A child of itself.
                    continue

            # Direct initiator
            if resource["initiator"].get("url") is not None:
                assign_direct_parent(resource, tree, current_root_node, node)

            # Else go through the stack and parents
            else:
                # Stack exists
                if resource["initiator"].get("stack") is not None:

                    assign_parent_from_callstack(current_resource, resource, \
                                                 tree, current_root_node, node)

                # Stack doesn't exist, just set last main page as the predecessor
                else:
                    current_root_node.add_child(node)

    return tree

def load_network_traffic_files() -> list[dict]:
    """Function to return observed network traffic  for each page as a record in dict
    
    Returns:
        list[dict]: List of loaded network logs
    """
    # Load all HTTP(S) traffic files from `./traffic/` folder
    network_files = get_traffic_files("network")

    traffic_logs = []
    for file in network_files:
        traffic = load_json(file)

        # obtain pure filename to be used as key for both FP files and resource tree
        pure_filename = os.path.basename(file)

        # Add name of the file as part of tuple
        traffic_logs.append((traffic, pure_filename))

    return traffic_logs


def create_trees(fp_attempts: dict, options: Config) -> dict[RequestTree]:
    """Function to load all HTTP traffic files and reconstruct request trees
    Also assigns observed fingerprinting attempts to each page
    
    Args:
        fp_attempts: Loaded dictionary of assigned FP attempts
        options: instance of Config

    Returns:
        dict[RequestTree]: Request trees with associated FP attempts
    """
    print("Reconstructing request trees...")

    trees = {}
    traffic_logs = load_network_traffic_files()
    total = len(traffic_logs)
    progress_printer = print_progress(total, "Creating request trees...")
    lower_bound_trees = options.lower_bound_trees

    for (traffic, traffic_file_number) in traffic_logs:
        progress_printer()

        # obtain corresponding FP attempts, in case of an error (should never happen)
        # return an empty dict with no FP attempts observed
        corresponding_fp_attempts = fp_attempts.get(traffic_file_number, {})
        trees[traffic_file_number] = reconstruct_tree(traffic, corresponding_fp_attempts,\
                                            lower_bound_trees)

    print("Request trees reconstructed!")
    return trees
