# request_node.py
# The class representing request node in a request tree.
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

class RequestNode:
    """Class representing each node in the request tree"""
    def __init__(self, time: str, resource: str, fp_attempts: dict,\
                 children: list["RequestNode"]=None) -> None:
        """Init method for setting up each instance'
        
        Args:
            time: Time at which network event occured
            resource: URL of the loaded resource (requested_resource)
            fp_attempts: FP attempts assigned to this resource
            children: list of children that should have this resource as parent
        """
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
        else:
            self.children = []

        # New node has initially no parent
        self.parents = []

    def is_blocked(self) -> bool:
        return self.blocked

    def block(self, transitive_block: bool=False) -> None:
        """Method to mark Node as blocked
        
        Args:
            transitive_block: Indicator that the block was result of transitive blocking.
                              Serves to differentiate if a resource should be blocked if not all
                              its parents are.
        """

        # Check if it has multiple parents - only block child if all of them are blocked
        # only do this for transitive requests
        if transitive_block:
            should_be_blocked = True
            for parent in self.get_parents():
                if not parent.is_blocked():
                    should_be_blocked = False

            # Only block if it was not a repeated transitive child and all its parents are blocked
            if not self.repeated and should_be_blocked:
                self.blocked = True

        # If it was not a transitive node, just block it
        else:
            self.blocked = True

    def set_fp_attempts(self, fp_attempts: dict) -> None:
        """Method to manually assign number of FP attempts to a resource
        
        Args:
            fp_attempts: dict containing FP attempts summarized in three primary categories
        """
        self.fp_attempts = fp_attempts

    def get_fp_attempts(self) -> dict:
        """Method to return the number of FP attempts associated with a given resource
        
        Returns:
            dict: FP attempts assigned to this Node
        """
        return self.fp_attempts

    def get_resource(self) -> str:
        """Method to return the URL of the resource stored in the node
        
        Returns: 
            str: URL assigned to this Node
        """
        return self.resource

    def get_time(self) -> str:
        """Method to return the timestamp of the resource stored in the node
        
        Returns:
            str: time at which the network event represented by this Node occured
        """
        return self.time

    def get_parents(self) -> list["RequestNode"]:
        """Method to return the parent of the node
        
        Returns:
            list: List of all parents of this Node
        """
        return self.parents

    def get_children(self) -> list["RequestNode"]:
        """Method to return all direct children of the node
        
        Returns:
            list: List of all children directly asigned to this Node
        """
        return self.children

    def _child_already_present(self, child_node: "RequestNode") -> bool:
        """Internal method to to avoid child duplicates
        
        Args:
            child_node: RequestNode which is tested if already among children of this Node
        
        Returns:
            bool: If given Node with URL is already a child node of this Node
        """
        children = self.get_children()
        for child in children:
            if child.get_resource() == child_node.get_resource():
                return True
        return False

    def add_child(self, child_node: "RequestNode") -> None:
        """"Method to add child node to a parent node
        
        Args:
            child_node: Node to be added as a child of this Node
        """
        # If the child node is already there, do not repeat
        if self._child_already_present(child_node):
            return

        self.children.append(child_node)
        child_node.add_parent(self)

    def add_parent(self, parent_node: "RequestNode") -> None:
        """Method to add parent to a child node
        
        Args:
            parent_node: Node to be added as a parent of this Node
        """
        # Do not add the same node as parent multiple times
        if parent_node in self.parents:
            return

        self.parents.append(parent_node)
        parent_node.add_child(self)

    def get_all_children_resources(self) -> list[str]:
        """Method to return all children resources of the node -> even transitively.
        Also contains the node resource itself.

        Returns:
           list: The children Nodes ordered by time they were logged.
        """
        children = self.get_all_children_nodes()

        # Sort the children by time, only do it once here
        children.sort(key=lambda child: int(child.get_time()))

        # Leave only the URLs
        children = list(map(lambda node: node.get_resource(), children))
        return children

    def get_all_children_nodes(self) -> list["RequestNode"]:
        """Method to return all children nodes of the current node -> even transitive
        Also contains the node itself
        
        Returns:
            list: All nodes even transitively associated as children of this Node
        """
        children = []

        # Add the current node resource
        children.append(self)

        for child in self.get_children():

            # Add the transitive children (children of children...)
            transitive_children = child.get_all_children_nodes()
            children.extend(transitive_children)

        return children
