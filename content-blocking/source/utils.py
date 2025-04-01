# utils.py
# Assortment of difficult-to-assign functions used across the program
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
import json

# Custom modules
from source.file_manipulation import get_traffic_files

def print_progress(total: int, message: str, limiter=10) -> None:
    """Function utilizing closure mechanism to print progress during for loops

    Args:
        total: Maximum progress to which count
        message: What to print with each message
        limiter: How often to print (modulo limiter, so 10 means 10%, 20%...)
    """
    progress_counter = 1
    previous_progress = -1

    def show_progress():
        """Function to return as the closure"""
        nonlocal progress_counter, previous_progress
        progress_percent = round(progress_counter/total, 2) * 100
        if (progress_percent % limiter == 0 and previous_progress != progress_percent):
            print(message, f"{progress_percent}%")

        previous_progress = progress_percent
        progress_counter += 1

    return show_progress

def squash_dns_records() -> dict:
    """Function to squash all observed DNS records into one list. Loads the records from files.
    
    Returns:
        dict: Dict containing DNS records from all observed files
    """

    print("Squashing DNS records...")
    # Get all DNS files in the ./traffic/ folder
    dns_files = get_traffic_files('dns')

    squashed_records = {}

    # Get records from each file and squash them together
    for file in dns_files:
        with open(file, 'r', encoding='utf-8') as f:
            dns_json = json.load(f)
            for (domain, value) in dns_json.items():

                # Should a key be observed multiple times, overwrite it (should be cached)
                if not squashed_records.get(domain):
                    squashed_records[domain] = value
                else:
                    for (subdomain, records) in dns_json[domain].items():
                        squashed_records[domain][subdomain] = records

    return squashed_records

def squash_tree_resources(request_trees: dict) -> list[str]:
    """Function to squash together resources from all observed request trees
    
    Args:
        request_trees: Trees to squash

    Returns:
        list[str]: All resources in the trees without duplicates
    """

    print("Squashing all tree resources...")
    resources = []

    # For each tree, get all requests
    for (key, _) in request_trees.items():
        resources.extend(request_trees[key].get_all_requests())

    # Remove duplicates
    resources = list(dict.fromkeys(resources))
    return resources

def add_substract_fp_attempts(callers_1: dict, callers_2: dict, add: bool=True) -> dict:
    """Function to add together 2 dicts with observed FP attempts
    
    Args:
        callers_1: First FP attempts dict
        callers_2: Second FP attempts dict
        add: Whether to add (True) or Substract (False)
    
    Returns:
        dict: Result of the selected operation
    """
    new_dict = {}

    # compatibility fix across analysis
    if isinstance(callers_1, int):
        callers_1 = {}

    if isinstance(callers_2, int):
        callers_2 = {}

    # Get the dict that is longer (one of them may be empty)
    longer_callers = callers_1 if len(callers_1.items()) >= len(callers_2.items()) else callers_2

    # If one of the dicts is empty, return the other
    if callers_1 == {} or callers_2 == {}:
        return longer_callers

    other_caller = callers_1 if longer_callers == callers_2 else callers_2

    # Else add them together (I assume both have correctly assigned values)

    for (group_name, group_fp_attempts) in longer_callers.items():
        other_attempts_count = other_caller.get(group_name)
        if add:
            new_dict[group_name] = group_fp_attempts + other_attempts_count
        else:
            new_dict[group_name] = group_fp_attempts - other_attempts_count
    return new_dict
