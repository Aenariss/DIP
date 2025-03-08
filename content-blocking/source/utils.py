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

def squash_tree_resources(request_trees: dict) -> list:
    """Function to squash together resources from all observed request trees"""
    resources = []

    # For each tree, get all requests
    for (key, _) in request_trees.items():
        resources.extend(request_trees[key].get_all_requests())

    # Remove duplicates
    resources = list(dict.fromkeys(resources))
    return resources
