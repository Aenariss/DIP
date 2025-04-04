# fp_attempts.py
# Assign number of FP attempts to a resource
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

# Custom modules
from source.constants import GENERAL_ERROR, FPD_WRAPPERS_FILE, FPD_GROUPS_FILE
from source.file_manipulation import load_json, get_traffic_files
from source.utils import print_progress

ANONYMOUS_CALLER = "<anonymous>"
TOP_LEVEL_FP_GROUP = "TOP_LEVEL"

def get_primary_groups(all_groups: dict) -> list:
    """Function to return all top-level primary groups from a dict of all groups
    
    Args:
        all_groups: All FPD groups specified in config file
    
    Returns:
        list: All top-level primary groups
    """
    primary_groups = []
    for (group_name, primary_group) in all_groups.items():
        if primary_group == TOP_LEVEL_FP_GROUP:
            primary_groups.append(group_name)
    return primary_groups

def construct_default_fp_value(primary_groups: list) -> dict:
    """Function to construct a default (empty) FP value for each loaded page
    
    Args:
        primary_groups: list of primary top-level groups in the FPD config
    
    Returns:
        dict: Each of the primary groups has assigned 0 observed attempts by default
    """
    default = {}
    for group in primary_groups:
        default[group] = 0
    return default

def parse_callers(all_callers: dict, fp_logs: dict, primary_group: list,\
                    all_primary_groups: list) -> dict:
    """Function to parse callstack of a property
    
    Args:
        all_callers: All resources responsible for calling the API
        fp_logs: All resources with assigned number of FP attempts
        primary_group: list of assigned primary groups for the processed API
        all_primary_groups: All top-level primary groups from the FPD config

    Returns:
        dict: Updated observed FP attempts caused by calling the parsed property
    """
    def parse_last_caller(last_caller: str) -> str:
        """Inline method to parse last caller string to obtain only the URL
        
        Args:
            last_caller: Line from error call stack containing the final caller
        
        Returns:
            str: URL of the caller extracted from the text-like callstack
        """

        # Split it by space and get the last
        split_by_space = last_caller.split(" ")
        final_last_caller = split_by_space[-1]

        # If it was an anonymous caller, check if there's an associated URL where
        # the anonymous funciton comes from.
        if final_last_caller.startswith(ANONYMOUS_CALLER):
            split_by_comma = last_caller.rsplit(",", 1)

            # If I could split it, the URL is the second to last part
            if len(split_by_comma) >= 2:
                second_to_last_part = split_by_comma[-2]

                # Now go through the part with the url
                return parse_last_caller(second_to_last_part)

        # Remove brackets in case they're there
        if (final_last_caller[0]) == '(':
            final_last_caller = final_last_caller[1:-1]

        # Split twice from the right, because last caller has formatting :1:1 (line number)
        final_last_caller = final_last_caller.rsplit(':', 2)

        final_last_caller = final_last_caller[0]

        return final_last_caller

    # Callstacks are still in the form of a key in dict, obtain it
    # Get all callers of a given property
    for (callers, _) in all_callers.items():

        # Split the callstack by a newline
        callstack = callers.split("\n")

        # Get the last caller
        last_caller = parse_last_caller(callstack[-1])

        # Each callstack means one more attempt, add it to the page attempts count
        current_page_fp = fp_logs.get(last_caller)

        # Page was not logged yet
        if not current_page_fp:
            fp_logs[last_caller] = construct_default_fp_value(all_primary_groups)
            for group in primary_group:
                fp_logs[last_caller][group] += 1

        # Page has already been observedd to attempt some FP
        else:
            for group in primary_group:
                fp_logs[last_caller][group] += 1

    return fp_logs

def parse_property_logs(primary_group: list, property_logs: dict, fp_logs: dict,\
                        all_primary_groups: list) -> dict:
    """Function to parse fingerprinting property data from the logs
    
    Args: 
        primary_group: Primary groups associated with a given FP API
        property_logs: Information about the API callers and total attempts...
        fp_logs: dict with FP attempts assigned to a observed resources
        all_primary_groups: All primary groups obtained from the FP config

    Returns:
        dict: Associated FP attempts to each logged resource
    """
    # Go throug call/get/set
    for (obtain_key, _) in property_logs.items():
        property_log_data = property_logs[obtain_key]

        # Obtain callers of the property -> if unavailable, return empty
        callers = property_log_data.get("callers", {})

        # Skip parsing empty callers, just add the total to <anonymous>
        if not callers:
            total = int(property_log_data.get("total", 0))

            # Check if anonymous caller is present already or not
            if fp_logs.get(ANONYMOUS_CALLER):
                for group in primary_group:
                    fp_logs[ANONYMOUS_CALLER][group] += total

            # If not inserted yet, create default value for all categories
            else:
                fp_logs[ANONYMOUS_CALLER] = construct_default_fp_value(all_primary_groups)
                for group in primary_group:
                    fp_logs[ANONYMOUS_CALLER][group] += total

        # The caller will be only the last page which actually called the API
        # Similar to the request tree, where predecessor is the last page in callstack
        fp_logs = parse_callers(callers, fp_logs, primary_group, all_primary_groups)

    return fp_logs

def get_fp_attempts(fp_data: dict, all_groups: dict, property_groups: dict) -> dict:
    """Function to get FP attempts from given FP file and return number address and its attempts
    
    Args:
        fp_data: FP attempts loaded from a given FPD log
        all_groups: FP groups loaded from configuration file with primary parents assigned
        property_groups: Wrapped APIs with assigned primary groups

    Returns:
        dict: All resources in FP logs with assigned number of FP attempts belonging
            to each of the primary groups
    """
    fp_logs = {}

    # Get primary groups to use during initialization of each resource
    primary_groups = get_primary_groups(all_groups)

    # Go through the log file and obtain access logs
    try:
        for (log_key, _) in fp_data.items():
            access_logs = fp_data[log_key]

            # Go through each logged site in the report
            for (site_key, _) in access_logs.items():
                site_data = access_logs[site_key]

                # Go through each FP property
                for (property_name, fp_property_logs) in site_data.items():
                    primary_group = property_groups.get(property_name)
                    fp_logs = parse_property_logs(primary_group, fp_property_logs, fp_logs,
                                                    primary_groups)

    except Exception as e:
        print(e)
        print("Could not load FP attempts from a FP logfile!")
        exit(GENERAL_ERROR)

    return fp_logs


def get_network_file(file: str) -> str:
    """Function to obtain name of corresponding network file from other traffic file
    
    Args:
        file: Name of the FP file

    Returns:
        str: Name of the corresponding network file
    """
    def handle_file_error(arr: list) -> None:
        """Internal function to handle errors in get_network_file
        
        Args:
            arr: name of the FP file, split into array
        """
        if len(arr) != 2:
            print("Problem obtaining corresponding network file! Could not parse from:", file)
            exit(GENERAL_ERROR)

    # 1_fp.json -> 1_fp, json
    file_and_extension = file.split('.')

    handle_file_error(file_and_extension)

    # 1_fp -> 1, fp
    file_number = file_and_extension[0].split('_')
    handle_file_error(file_number)
    corresponding_filename = file_number[0] + "_network.json"

    return corresponding_filename

def assign_property_group(fp_groups: dict) -> dict:
    """Function to assign each wrapped property its primary parent group(s)
    
    Args:
        fp_groups: dict with all groups from FP configuration. 
            Each group has assigned primary parent

    Returns:
        dict: Dict with key being all wrapped APIs and value being their primary parent group
    """
    def get_primary_group(group_name: str, fp_groups: dict) -> str:
        """Internal method to find primary parent for a given group
        
        Args:
            group_name: Name of the group we are searching primary parent for
            fp_groups: All loaded groups with assigned parents

        Returns:
            str: name of the primary parent group
        """
        primary_name = fp_groups.get(group_name, None)

        if primary_name:
            # Check if it isnt top-level parent, if so, return the parent themselves
            if primary_name == TOP_LEVEL_FP_GROUP:
                return group_name

            # If it isnt, return the primary parent
            return primary_name

        # If primary name is unknown (should not happen), it ssignalizes wrong file format
        print("Error parsing FP files! Are files in ./source/traffic_parser/fp_files/ valid?")
        exit(GENERAL_ERROR)

    wrapped_properties = load_json(FPD_WRAPPERS_FILE)

    # Each property may have multiple primary parent groups
    properties_groups = {}

    for wrapped_property in wrapped_properties:
        property_name = wrapped_property.get("resource")
        assigned_groups = wrapped_property.get("groups")

        # Go through all assigned groups
        if assigned_groups:
            for group in assigned_groups:
                group_name = group.get("group")
                primary_group = get_primary_group(group_name, fp_groups)

                # Check if property already has group assigned
                if properties_groups.get(property_name):

                    # Only assign value if it isnt already present to avoid duplicates
                    if primary_group not in properties_groups[property_name]:
                        properties_groups[property_name].append(primary_group)
                else:
                    properties_groups[property_name] = [primary_group]

    return properties_groups

def obtain_fp_groups() -> dict:
    """Function to load the fpd groups file and assign each subgroup its primary parent group
    
    Returns:
        dict: All FPD Groups in a dict with the value of each group being their primary
        parent group (one of the three BrowserProperties, AlgorithmicMethods, CrawlFpInspector) 
    """
    def get_subgroups(subgroups: list, found_groups: dict, parent: str) -> dict:
        """Internal fuinction to recursively obtain subgroups of a group and set their parent
        
        Args:
            subgroup: list of subgroups of a given parent group
            found_groups: dict with existing assigned groups
            parent: name of the parent class which contains the subgroups

        Returns:
            dict: Dict with newly assigned parent group
        """

        # Go through all current-level groups
        for group in subgroups:
            group_name = group.get("name")
            found_groups[group_name] = parent

            next_level_subgroup = group.get("groups", [])

            # Recursively go through all child subgroups
            if next_level_subgroup:
                found_groups = get_subgroups(next_level_subgroup, found_groups, parent)

        return found_groups

    groups = load_json(FPD_GROUPS_FILE)

    # Get groups of the first level (BrowserProperties...)
    first_level_groups = groups.get("groups")
    found_grups = {}

    # Go through all first level groups and set their subgroup parent as the group
    for top_level_group in first_level_groups:
        main_group = top_level_group.get("groups", [])
        parent_name = top_level_group.get("name")

        # Set parent of the top level groups as specific value
        found_grups[parent_name] = TOP_LEVEL_FP_GROUP

        # Recursively go through each subgroup
        if main_group:
            found_grups = get_subgroups(main_group, found_grups, parent_name)

    return found_grups

def parse_fp() -> dict:
    """Function to load FP attempts from a corresponding file and
    assign each domain a nuimber of observed attempts.
    
    Returns:
        dict: Assigned total FP attempts to each site
    """

    # First obtain all groups from JShelter FPD groups file
    # For child groups, assign them their primary parent group. Parent group itself has no parent
    fp_groups = obtain_fp_groups()

    # Go through all wrappers and assign each wrapped property its primary group
    fp_wrappers = assign_property_group(fp_groups)

    # Get FP files from traffic folder
    print("Assigning FP attempts to each site...")

    fp_files = get_traffic_files('fp')

    fp_attempts = {}

    progress_printer = print_progress(len(fp_files), "Loading FP attempts...")

    for file in fp_files:
        progress_printer()
        pure_filename = os.path.basename(file)
        corresponding_network_file = get_network_file(pure_filename)

        fp_data = load_json(file)

        fp_attempts[corresponding_network_file] = get_fp_attempts(fp_data, fp_groups, fp_wrappers)

    print("Finished assigning FP attempts to each site!")
    return fp_attempts
