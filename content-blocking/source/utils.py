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
    Total serves as the maximum progress
    Limiter defines when the progress is printed by modulo -> 10 means 0%, 10%, 20%... so on"""
    progress_counter = 0
    previous_progress = -1

    def show_progress():
        """Function to return as the closure"""
        nonlocal progress_counter, previous_progress
        progress_percent = round(progress_counter/total, 2) * 100
        if progress_percent % limiter == 0 and previous_progress != progress_percent:
            print(message, f"{progress_percent}%")

        previous_progress = progress_percent
        progress_counter += 1

    return show_progress

def squash_dns_records() -> dict:
    """Function to squash all observed DNS records into one list"""

    print("Squashing DNS records...")
    # Get all DNS files in the ./traffic/ folder
    dns_files = get_traffic_files('dns')

    squashed_records = {}

    # Get records from each file and squash them together
    for file in dns_files:
        with open(file, 'r', encoding='utf-8') as f:
            dns_json = json.load(f)
            for (domain, value) in dns_json.items():

                # Should a key be observed multiple times, append it overwrite it (should be cached)
                if not squashed_records.get(domain):
                    squashed_records[domain] = value
                else:
                    for (subdomain, records) in dns_json[domain].items():
                        squashed_records[domain][subdomain] = records

    return squashed_records

def squash_tree_resources(request_trees: dict) -> list[str]:
    """Function to squash together resources from all observed request trees"""

    print("Squashing all tree resources...")
    resources = []

    # For each tree, get all requests
    for (key, _) in request_trees.items():
        resources.extend(request_trees[key].get_all_requests())

    # Remove duplicates
    resources = list(dict.fromkeys(resources))
    return resources

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