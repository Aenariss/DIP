# request_tree.py
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
from source.utils import print_progress
from source.config import Config

ANONYMOUS_CALLERS = "<anonymous>"

class RequestNode:
    """Class representing each node in the request tree"""
    def __init__(self, time: str, resource: str, fp_attempts: dict,\
                 children: list["RequestNode"]=None) -> None:
        """Init method for setting up each instance"""
        self.resource = resource
        self.children = children
        self.time = time

        self.root_node = False
        self.repeated = False

        # Number of observed FP attempts used by this resource
        self.fp_attempts = fp_attempts

        # To be used later when calculating impact of blocking a resource
        # Represents whether this resource would have been blocked or not
        self.blocked = False

        # In case children were specified, correctly set-up the parent-child relation
        if children:
            for child in children:
                child.add_parent(self)

        # New node has initially no parent
        self.parents = []

    def is_blocked(self) -> bool:
        return self.blocked

    def block(self) -> None:
        # Only block if it was not a repeated node (cant say for 100% such node would be blocked)
        if not self.repeated:
            self.blocked = True

    def set_fp_attempts(self, fp_attempts: dict) -> None:
        """Method to manually assign number of FP attempts to a resource"""
        self.fp_attempts = fp_attempts

    def get_fp_attempts(self) -> dict:
        """Method to return the number of FP attempts associated with a given resource"""
        return self.fp_attempts

    def get_resource(self) -> str:
        """Method to return the URL of the resource stored in the node"""
        return self.resource

    def get_time(self) -> str:
        """Method to return the timestamp of the resource stored in the node"""
        return self.time

    def get_parents(self) -> list["RequestNode"]:
        """Method to return the parent of the node"""
        return self.parents

    def get_children(self) -> list["RequestNode"]:
        """Method to return all direct children of the node"""
        return self.children

    def __child_already_present(self, child_node: "RequestNode") -> bool:
        """Internal method to to avoid child duplicates"""
        children = self.get_children()
        for child in children:
            if child.get_resource() == child_node.get_resource():
                return True
        return False

    def __parent_already_present(self, parent_node: "RequestNode") -> bool:
        """Internal method to avoid parent duplicates"""
        parents = self.get_parents()
        for parent in parents:
            if parent.get_resource() == parent_node.get_resource():
                return True
        return False

    def add_child(self, child_node: "RequestNode") -> None:
        """"Method to add child node to a parent node"""
        # If the child node is already there, do not repeat
        if self.__child_already_present(child_node):
            return

        self.children.append(child_node)
        child_node.add_parent(self)

    def add_parent(self, parent_node: "RequestNode") -> None:
        """Method to add parent to a child node"""
        if not self.get_parents():
            self.parents.append(parent_node)
        else:
            # Check if the parent isn't alreaddy defined to avoid duplicates
            if self.__parent_already_present(parent_node):
                return
            self.parents.append(parent_node)

    def get_all_children_resources(self) -> list[str]:
        """Method to return all children resources of the node -> even transitively.
           Also contains the node resource itself.
           Returns the children resources ordered by time they were logged.
        """
        children = self.get_all_children_nodes()

        # Sort the children by time, only do it once here
        children.sort(key=lambda child: int(child.get_time()))

        # Leave only the URLs
        children = list(map(lambda node: node.get_resource(), children))
        return children

    def get_all_children_nodes(self) -> list["RequestNode"]:
        """Method to return all children nodes of the current node -> even transitive
           Also contains the node itself"""
        children = []

        # Add the current node resource
        children.append(self)

        for child in self.get_children():

            # Add the transitive children (children of children...)
            transitive_children = child.get_all_children_nodes()
            children.extend(transitive_children)

        return children

class RequestTree:
    """Class representing the whole tree-like request chain"""
    def __init__(self, root_node: RequestNode) -> None:
        self.root_node = root_node

    def get_root(self) -> RequestNode:
        """Method to retunr the root of the tree (initial page URL)"""
        return self.root_node

    def total_fpd_attempts(self, start: RequestNode=None) -> dict:
        """Method to calculate total number of FPD attempts observed in a tree"""
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
        """Method to calculate number of FPD attempts blocked at first blocked parent"""
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
        """Method to calculate total number of FPD attempts blockedd in a tree"""
        if start is None:
            start = self.get_root()

        blocked_attempts = {}

        # If starting node is blocked, return it as an array
        if start.is_blocked():
            blocked_attempts = add_substract_fp_attempts(start.get_fp_attempts(), blocked_attempts)

        # If start was not blocked, repeat for all children
        for child in start.get_children():
            blocked_attempts = add_substract_fp_attempts(
                self.total_blocked_fpd_attempts(start=child), blocked_attempts)

        return blocked_attempts

    def blocked_at_levels(self, start: RequestNode=None, level: int=1) -> list[int]:
        """Method to return levels at which first block in chain was observed"""
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
        resources"""
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
        """Method to compute the total number of blocked resources in a tree"""
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
        """Method to recursively get all resources requested on a page"""

        resource_list = []
        if not start_node:
            start_node = self.get_root()

        children = start_node.get_all_children_resources()
        resource_list.extend(children)

        return resource_list

    def __recursive_node_check(self, node: RequestNode, searched_resource: str)\
        -> list[RequestNode]:
        """Internal method to recursively check if a resource URL is present in the tree"""

        results = []

        # The node is what we're searching for - return it immediatly, resource\
        # can't have itself as a child
        if node.get_resource() == searched_resource:
            return [node]

        # Else recursively continue with children and return all matches
        for child_node in node.get_children():
            result = self.__recursive_node_check(child_node, searched_resource)
            if result:
                results.extend(result)
        return results

    def find_nodes(self, searched_resource: str) -> list[RequestNode]:
        """Method to check if a resource is present in the tree and return nodes that contain it"""
        return self.__recursive_node_check(self.get_root(), searched_resource)

    def print_tree(self, level: int=1, current_node: RequestNode=None, printing: bool=False) -> str:
        """Method to CLI-visualize the requests in a given tree or return the visualization as
        a string"""

        # Print the initial request - tree root
        result = ""
        if not current_node:
            current_fp_attempts = str(self.get_root().get_fp_attempts())
            block_result = "-- Blocked" if self.get_root().is_blocked() else "-- Loaded"
            if printing:
                print('--' * level, self.get_root().get_resource(), block_result,\
                       current_fp_attempts)

            # Add current level to result
            result += '\n' + '--' * level + ' ' + self.get_root().get_resource()\
                + ' ' + block_result + ' ' + current_fp_attempts

            # Recursively print for children
            for child in self.get_root().get_children():
                result += self.print_tree(level=level+1, current_node=child, printing=printing)

        # Other requests - child nodes
        else:
            current_fp_attempts = str(current_node.get_fp_attempts())
            block_result = "-- Blocked" if current_node.is_blocked() else "-- Loaded"
            if printing:
                print('|' + '--' * 2 * level + ' ' + current_node.get_resource()[:100]\
                     + ' ' + block_result + ' ' + current_fp_attempts)
            # Add current level to result
            result += '\n|' + '--' * 2 * level + ' ' + current_node.get_resource()[:100] + ' '\
                    + block_result + ' ' + current_fp_attempts

            # Recursively print for children
            for child in current_node.get_children():
                result += self.print_tree(level=level+1, current_node=child, printing=printing)
        return result

def fix_missing_parent(global_node: RequestNode, resource_node: RequestNode) -> None:
    """handle initiator when child resource was loaded before the parent, should rarely happen"""

    # If parent was not found, it might be because of some javascript-magic or because of iframes
    # that open for about:srcdoc or something like that. In that case, I'm unable to tell.
    # So just add it as parent of the root resource
    global_node.add_child(resource_node)

def join_call_frames(stack: dict) -> list[str]:
    """Function to recursively obtain the callstack containing all parents"""
    frames = []

    # Recursively obtain all parents if they exist
    # Go from the bottom -> Deepest parent first
    parent = stack.get("parent")
    if parent:
        deeper_parents = join_call_frames(parent)
        frames.extend(deeper_parents)

    # Add results from the current callframe
    # Reverse the list because the first in the stack is the final which caused it
    current_callframe = stack.get("callFrames", [])[::-1]
    for call in current_callframe:
        frames.append(call["url"])

    return frames

def add_substract_fp_attempts(callers1: dict, callers2: dict, add: bool=True) -> dict:
    """Function to add together 2 dicts with observed FP attempts"""
    new_dict = {}

    # compatibility fix across analysis
    if isinstance(callers1, int):
        callers1 = {}

    if isinstance(callers2, int):
        callers2 = {}

    # Get the dict that is longer (one of them may be empty)
    longer_callers = callers1 if len(callers1.items()) >= len(callers2.items()) else callers2

    # If one of the dicts is empty, return the other
    if callers1 == {} or callers2 == {}:
        return longer_callers

    other_caller = callers1 if longer_callers == callers2 else callers2

    # Else add them together (I assume both have correctly assigned values)

    for (group_name, group_fp_attempts) in longer_callers.items():
        other_attempts_count = other_caller.get(group_name)
        if add:
            new_dict[group_name] = group_fp_attempts + other_attempts_count
        else:
            new_dict[group_name] = group_fp_attempts - other_attempts_count
    return new_dict

def construct_tree(tree: RequestTree, resource_counter: int, node: RequestNode,\
                global_level: RequestNode, fp_attempts: dict, lower_bound_trees: bool)\
                -> tuple[RequestTree, RequestNode]:
    """Function to update global level and create a tree if it's the very first primary request"""

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
                return tree, global_level

            global_level.add_child(node)

            # Remove FP attempts that are associated with this node, since it is a duplicate
            # They are already associated with the main node
            node.set_fp_attempts({})

            return tree, global_level

        global_level.add_child(node)
        node.root_node = True

        # Delete all anonymous FP attempts from the previous root node and add them to the new one
        root_fp_attempts = global_level.get_fp_attempts()
        previous_root_node_fp_attempts = add_substract_fp_attempts(root_fp_attempts,\
                                                         anonymous_attempts, add=False)
        global_level.set_fp_attempts(previous_root_node_fp_attempts)

        new_root_node_fp_attempts = node.get_fp_attempts()
        with_anonymous_callers = add_substract_fp_attempts(new_root_node_fp_attempts,\
                                                           anonymous_attempts)

        node.set_fp_attempts(with_anonymous_callers)

    global_level = node
    return tree, global_level

def reconstruct_tree(observed_traffic: dict, fp_attempts: dict, lower_bound_trees: bool)\
      -> RequestTree:
    """Function to reconstruct initiator chains from observed traffic and assign FP
    attempts to each page"""
    tree = None
    requests_count = len(observed_traffic)
    global_level = None

    for resource_number in range(requests_count):
        resource = observed_traffic[resource_number]
        current_resource = resource["requested_resource"]
        # If time is unavailable, use maximum
        time = resource.get("time", sys.maxsize)

        # Either get number of observed FP attempts or 0 if none observed
        resource_fp_attempts = fp_attempts.get(current_resource, {})

        # Create new Node object representing the resource. Creates duplicit requests!!
        # Check if node already exists, if so, at least do not assign it FP attempts
        node = RequestNode(time, current_resource, fp_attempts=resource_fp_attempts, children=[])

        # If requested_for matches requested_resource and initiator type is "other"
        # it's probably a redirect and go globally a level deeper, also mark it as root node
        if resource["requested_for"] == current_resource and\
            resource["initiator"]["type"] == "other":

            tree, global_level = construct_tree(tree, resource_number,\
                                        node, global_level, fp_attempts, lower_bound_trees)

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

                # Skip preflights since they will be loaded later anyway
                if resource["initiator"]["type"] == "preflight":
                    continue

                # Check if the parent is already present
                parent_nodes = tree.find_nodes(resource["initiator"]["url"])

                # Parent not known should not happen often (child resource loaded before parent)
                if not parent_nodes:
                    # If it was not preflight, it's strange, so handle it
                    fix_missing_parent(global_level, node)

                # Parent present, add it as their child
                else:
                    # Resource can be requested by multiple requests -> very weird!
                    if len(parent_nodes) > 1:
                        pass

                    # Problem - how do I know which parent is the correct one?
                    # A was requested 7 times by different resources. A requested B. Which from the
                    # 7 A is responsible? Assign to all.
                    for parent_node in parent_nodes:
                        parent_node.add_child(node)


            # Else go through the stack and parents
            else:
                # Stack exists
                if resource["initiator"].get("stack") is not None:

                    # Concatenate all call stacks
                    calls = join_call_frames(resource["initiator"]["stack"])

                    # Add the loaded resource to the end
                    calls.append(current_resource)

                    # Situation like A -> B -> A -> C may occur
                    # Fix it by removing duplicates and leaving just A -> B -> C
                    # transitive logic remains intact
                    # Chrome DevTools (F12 Initiators) does not do this
                    #calls = list(dict.fromkeys(calls))

                    # Remove dynamic content with no known initiator
                    # and chrome-extension JShelter wrappers
                    # "" -> B -> C = just B -> C
                    calls = [x for x in calls if (x != '') and not x.startswith("chrome-extension")]

                    # Obtain only the direct initiator - only look for the final request that
                    # caused the resource to be loaded. Seems to work, tbd: ensure it does
                    last_two_calls = calls[-2:]

                    if len(last_two_calls) == 2:

                        # Check if the parent is already known (should be)
                        parent_nodes = tree.find_nodes(last_two_calls[0])

                        for parent_node in parent_nodes:
                            parent_node.add_child(node)

                        # If parent unknown, try to fix it (should not happen)
                        if parent_nodes == []:
                            fix_missing_parent(global_level, node)

                    # If all callframes were empty (dynamic), just set the last
                    # global level as parent of the resource
                    if len(calls) == 1:
                        global_level.add_child(node)

                # Stack doesn't exist, just set last main page as the predecessor
                else:
                    global_level.add_child(node)

    return tree

def create_trees(fp_attempts: dict, options: Config) -> dict:
    """Function to load all HTTP traffic files and reconstruct request trees
    Also assigns observed fingerprinting attempts to each page"""
    print("Reconstructing request trees...")

    trees = {}

    # Load all HTTP(S) traffic files from `./traffic/` folder
    network_files = get_traffic_files("network")

    total = len(network_files)
    progress_printer = print_progress(total, "Creating request trees...")

    lower_bound_trees = options.lower_bound_trees

    for file in network_files:
        progress_printer()
        traffic = load_json(file)

        # obtain pure filename to be used as key for both FP files and resource tree
        pure_filename = os.path.basename(file)

        # obtain corresponding FP attempts, in case of an error (should never happen)
        # return an empty dict with no FP attempts observed
        corresponding_fp_attempts = fp_attempts.get(pure_filename, {})
        trees[pure_filename] = reconstruct_tree(traffic, corresponding_fp_attempts,\
                                            lower_bound_trees)

    print("Request trees reconstructed!")
    return trees
