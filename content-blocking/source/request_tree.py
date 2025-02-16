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
from source.file_loading import load_json
from source.constants import TRAFFIC_FOLDER

class RequestNode:
    """Class representing each node in the request tree"""
    def __init__(self, time: str, resource: str,\
                 children: list["RequestNode"]=None) -> None:
        """Init method for setting up each instance"""
        self.resource = resource
        self.children = children
        self.time = time

        # To be used later when calculating impact of blocking a resource
        # Represents whether this resource would have been blocked or not
        self.blocked = False

        # In case children were specified, correctly set-up the parent-child relation
        if children:
            for child in children:
                child.add_parent(self)

        # New node has initially no parent
        self.parent = None

    def is_blocked(self) -> bool:
        return self.blocked

    def block(self) -> None:
        self.blocked = True

    def get_resource(self) -> str:
        """Method to return the URL of the resource stored in the node"""
        return self.resource

    def get_time(self) -> str:
        """Method to return the timestamp of the resource stored in the node"""
        return self.time

    def get_parent(self) -> "RequestNode":
        """Method to return the parent of the node"""
        return self.parent

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
        parent = self.get_parent()
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
        if self.parent is None:
            self.parent = parent_node
        else:
            # Check if the parent isn't alreaddy defined to avoid duplicates
            if self.__parent_already_present(parent_node):
                return
            self.parent = parent_node

    def get_all_children(self) -> list[str]:
        """Method to return all children resources of the node -> even transitively.
           Also contains the node resource itself.
           Returns the children resources ordered by time they were logged.
        """
        children = self.recursion_get_all_children()

        # Sort the children by time, only do it once here
        children.sort(key=lambda child: int(child.get_time()))

        # Leave only the URLs
        children = list(map(lambda node: node.get_resource(), children))
        return children

    def get_all_children_nodes(self) -> list["RequestNode"]:
        """Method to return all children nodes of the current node -> even transitive
           Also contains the node itself"""
        return self.recursion_get_all_children()

    def recursion_get_all_children(self) -> list["RequestNode"]:
        """Internal method to return all children of the node -- even transitively"""
        children = []

        # Add the current node resource
        children.append(self)

        for child in self.get_children():

            # Add the transitive children (children of children...)
            transitive_children = child.recursion_get_all_children()
            children.extend(transitive_children)

        return children

class RequestTree:
    """Class representing the whole tree-like request chain"""
    def __init__(self, root_node: RequestNode) -> None:
        self.root_node = root_node

    def get_root(self) -> RequestNode:
        """Method to retunr the root of the tree (initial page URL)"""
        return self.root_node

    def number_of_blocked(self, start: RequestNode=None) -> int:
        """Method to compute the total number of blocked resources in a tree"""
        if start is None:
            start = self.get_root()

        blocked = 0

        # Check if the initial node is blocked
        if start.is_blocked():
            blocked += 1

        # For each child calculate how many of its children are blocked
        for child in start.get_children():
            blocked = blocked + self.number_of_blocked(start=child)

        return blocked

    def calculate_blocked(self, blocked_resources: list[str]) -> tuple[int, int]:
        """Method to calculate how many resources in total would have been blocked, had the
        resoureces present in blocked_resources would have been blocked.
        Returns the number of requests that would have been blocked and number of 
        fp attempts blocked by association"""

        # First, block only parent nodes to obtain how many would be observed without request chain
        for resource in blocked_resources:
            nodes_with_resource = self.find_nodes(resource)
            for node in nodes_with_resource:

                # Mark initial node as blocked
                node.block()
        
        # Obtain number of blocked requests in the tree with no recursive blocking
        blocked_not_transitive = self.number_of_blocked()

        # Second, block all child nodes transitively if parent is blocked
        # Go through each blocked resource and check if its present in the tree
        for resource in blocked_resources:
            nodes_with_resource = self.find_nodes(resource)
            for parent_node in nodes_with_resource:

                # Mark initial node as blocked
                parent_node.block()

                # Also mark all children as blocked
                child_nodes = parent_node.get_all_children_nodes()
                for node in child_nodes:
                    node.block()

        # Go through the whole tree and calculate numer of blocked
        blocked_resources = self.number_of_blocked()

        return blocked_resources, blocked_not_transitive, 0


    def get_all_requests(self, start_node: RequestNode=None) -> list[RequestNode]:
        """Method to recursively get all resources requested on a page"""

        resource_list = []
        if not start_node:
            start_node = self.get_root()

        children = start_node.get_all_children()
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
        """Method to CLI-visualize the requests in a given tree or return the tree as a string"""

        # Print the initial request - tree root
        result = ""
        if not current_node:
            block_result = "-- Blocked" if self.get_root().is_blocked() else "-- Loaded"
            if printing:
                print('--' * level, self.get_root().get_resource(), block_result)

            # Add current level to result
            result += '\n' + '--' * level + ' ' + self.get_root().get_resource()\
                + ' ' + block_result

            # Recursively print for children
            for child in self.get_root().get_children():
                result += self.print_tree(level=level+1, current_node=child, printing=printing)

        # Other requests - child nodes
        else:
            block_result = "-- Blocked" if current_node.is_blocked() else "-- Loaded"
            if printing:
                print('|' + '--' * 2 * level + ' ' + current_node.get_resource()[:100]\
                     + ' ' + block_result)
                    #"<-", ' '.join(x.get_resource()[:100] for x in current_node.get_parent()))
            # Add current level to result
            result += '\n|' + '--' * 2 * level + ' ' + current_node.get_resource()[:100] + ' '\
                    + block_result

            # Recursively print for children
            for child in current_node.get_children():
                result += self.print_tree(level=level+1, current_node=child, printing=printing)
        return result

def fix_missing_parent(observed_traffic: dict, resource: dict, tree: RequestTree,\
                       previous_main_node: RequestNode, node: RequestNode) -> None:
    """Fix initiator when child resource was loaded before the parent, should rarely happen"""

    # Find every parent resource that requested the resource
    direct_parents = look_for_specific_initiator(observed_traffic,\
                                                resource["initiator"]["url"])
    time = resource.get("time", sys.maxsize)
    new_parent_node = RequestNode(time, resource["initiator"]["url"], children=[node])

    # If direct parent wasnt found, set current root as the parent
    # (maybe look recursively deeper instead?)
    if not direct_parents:
        previous_main_node.add_child(new_parent_node)

    # Else find the parent of the parent
    else:
        for parent_node in direct_parents:
            # Parents who requsted the parent of the current resource
            parent_nodes = tree.find_nodes(parent_node["initiator"]["url"])
            for parent_node in parent_nodes:
                parent_node.add_child(new_parent_node)

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

def construct_tree(tree: RequestTree, resource_counter: int, node: RequestNode,\
                    global_level: RequestNode) -> tuple[RequestTree, RequestNode]:
    """Function to update global level and create a tree if it's the very first primary request"""
    if resource_counter == 0:
        tree = RequestTree(node)

    else:
        # Check if the request is not to a page already in the tree ->
        # It is unnecessary for the analysis and makes results weird.
        # Just add it as a regular child of the previous global level
        if tree.find_nodes(node.get_resource()):

            global_level.add_child(node)
            return tree, global_level
        
        global_level.add_child(node)

    global_level = node
    return tree, global_level

def reconstruct_tree(observed_traffic: dict) -> RequestTree:
    tree = None
    requests_count = len(observed_traffic)
    global_level = None

    for resource_number in range(requests_count):
        resource = observed_traffic[resource_number]
        current_resource = resource["requested_resource"]
        # If time is unavailable, use maximum
        time = resource.get("time", sys.maxsize)
        node = RequestNode(time, current_resource, children=[])

        # If requested_by matches requested_resource and initiator type is "other"
        # it's a redirect and go globally a level deeper
        if resource["requested_by"] == current_resource and\
            resource["initiator"]["type"] == "other":

            tree, global_level = construct_tree(tree, resource_number, node, global_level)

        else:
            # Direct initiator
            if resource["initiator"].get("url") is not None:

                # Check if the parent is already present
                parent_nodes = tree.find_nodes(resource["initiator"]["url"])

                # Parent not known should not happen often (child resource loaded before parent)
                # May happen with some preflights -- I'll skip those since they will be already loaded anyway
                if not parent_nodes:
                    if resource["initiator"]["type"] == "preflight":
                        continue

                    # If it was not preflight, it's strange, but try to fix it
                    fix_missing_parent(observed_traffic, resource, tree, global_level, node)

                # Parent present, add it as their child
                else:
                    # Resource can be requested by multiple requests - its a child of all of them
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
                    # "" -> B -> C = just B -> C
                    calls = [x for x in calls if x != '']

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
                            fix_missing_parent(observed_traffic,\
                                {"initiator": {"url":last_two_calls[1]}}, tree, global_level, node)

                    # If all callframes were empty (dynamic), just set the last
                    # global level as parent of the resource
                    if len(calls) == 1:
                        global_level.add_child(node)

                # Stack doesn't exist, just set last main page as the predecessor
                else:
                    global_level.add_child(node)

    return tree

def look_for_specific_initiator(traffic: dict, find: str) -> dict:
    """Function to find the direct initiator of a specific resource"""
    requests_count = len(traffic)
    results = []
    for resource_number in range(requests_count):
        resource = traffic[resource_number]
        if resource["initiator"].get("url") is not None:
            if resource["requested_resource"] == find:
                results.append(resource)
    return results

def create_trees() -> dict:
    """Function to load all HTTP traffic files and reconstruct request trees"""
    print("Reconstructing request trees...")

    trees = {}

    # Load all HTTP(S) traffic files from `./traffic/` folder
    for file in os.listdir(TRAFFIC_FOLDER):
        file_with_extension = file.split('.')
        if len(file_with_extension) == 2:
            if file_with_extension[1] == "json":
                if file_with_extension[0][-3:] != "dns":
                    traffic = load_json(TRAFFIC_FOLDER + file)
                    trees[file] = reconstruct_tree(traffic)

    print("Request trees reconstructed!")
    return trees
