# start.py
# The driver program that launches the testing.
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
import argparse
import os
import json

# Custom modules
from source.constants import TRAFFIC_FOLDER, GENERAL_ERROR, OPTIONS_FILE, RESULTS_FOLDER
from source.load_traffic import load_traffic
from source.request_tree import create_trees
from source.test_page_server import start_testing_server, stop_testing_server
from source.visit_test_server import visit_test_server
from source.calculate_blocked import calculate_blocked
from custom_dns_server.dns_repeater_server import DNSRepeater

# Argument parsing
parser = argparse.ArgumentParser(prog="Content-blocking evaluation",
                                 description="Evaluates given content-blocking\
                                      tools on given pages")
parser.add_argument('-l', '--load', action="store_true",
                    help="Whether to observe network traffic anew using page_list.txt")
parser.add_argument('-c', '--compact', action="store_true",
            help="Whether to store only required data during load (does not change functionality)")
parser.add_argument('-lo', '--load-only', action="store_true",
            help="Whether to only observe network traffic anew using page_list.txt and stop")
args = parser.parse_args()

def initialize_folders() -> dict:
    """Function to prepare folderes to be used during evaluation. Returns user options."""

    # Load options for the evaluation
    if not os.path.exists(OPTIONS_FILE):
        print("Could not load ``options.json`` file!")

    with open(OPTIONS_FILE, encoding="utf-8") as f:
        options = json.load(f)

    # If load or load-only was specified, prepare folders accordingly
    if args.load or args.load_only:
        # (Re)create the traffic folder
        if not os.path.exists(TRAFFIC_FOLDER):
            print("Creating the traffic folder...")
            os.makedirs(TRAFFIC_FOLDER)
            f = open(TRAFFIC_FOLDER + ".empty", 'w', encoding='utf-8')
            f.close()

        # Delete existing logs if the folder exists
        else:
            print("Removing existing traffic files...")
            for file in os.listdir(TRAFFIC_FOLDER):
                filename = TRAFFIC_FOLDER + file

                # Remove existing file except for the placeholder file
                if os.path.isfile(filename) and file != ".empty":
                    os.remove(filename)

    return options

def check_traffic_folder() -> None:
    """Function to check that trafficc folder is present and not empty"""

    # Check that the traffic folder exists
    if not os.path.exists(TRAFFIC_FOLDER):
        print("Couldn't find the folder with the observed traffic!\n" +
              "Run the program with '--load' argument first!")
        exit(GENERAL_ERROR)
    else:
        # If the traffic folder is empty (only the .empty file), it needs to be loaded
        if len([file for file in os.listdir(TRAFFIC_FOLDER)
                if os.path.isfile(TRAFFIC_FOLDER + file)]) == 1:
            print("Couldn't find the folder with the observed traffic!\n" +
                "Did you specify at least 1 page in the ``page_list.txt`` file? " +
                "If so, run the program with '--load' argument first!")
            exit(GENERAL_ERROR)

def squash_dns_records() -> dict:
    """Function to squash all observed DNS records into one list"""

    # Get all DNS files in the ./traffic/ folder
    dns_files = [file for file in os.listdir(TRAFFIC_FOLDER) if "_dns" in file]

    squashed_records = {}

    # Get records from each file and squash them together
    for file in dns_files:
        file = TRAFFIC_FOLDER + file
        with open(file, 'r', encoding='utf-8') as f:
            dns_json = json.load(f)
            for (key, value) in dns_json.items():

                # Should a key be observed multiple times, overwrite it (should be cached)
                squashed_records[key] = value
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

def start() -> None:
    """Main driver function"""

    # Check user arguments were correct
    if args.load:
        if args.load_only:
            print("You can only use one argument! Either '--load' or '--load-only'!")
            exit(GENERAL_ERROR)

    # Load user options
    options = initialize_folders()

    # If load or load-only was specified, go through the specified pages and observe traffic
    if args.load or args.load_only:

        print("Loading the traffic...")
        load_traffic(options, args.compact)
        print("Traffic loading finished!")

        # if load-only was specified, don't do anything else and quit
        if args.load_only:
            return

    # Check traffic folder is present and not empty
    check_traffic_folder()

    # Create initiator tree-like chains from data in the ./traffic/ folder
    request_trees = create_trees()

    # Squash DNS records and contacted pages from all observations together
    dns_records = squash_dns_records()
    resource_list = squash_tree_resources(request_trees)

    # Start the DNS server and set it as prefered to repeat responses
    #dns_repeater = DNSRepeater(dns_records)
    #dns_repeater.start()
    #dns_repeater.stop()
    input("Press any key to stop...")
    return

    # Start the testing server as another process for each logged page traffic
    server = start_testing_server(resource_list)

    # Visit the server and log the console outputs
    console_output = visit_test_server(key, {}, resource_list)

    # Calculate how many requests in the chain would have been blocked
    blocked_total, blocked_not_transitive, blocked_fp_attempts = calculate_blocked(request_trees[key], console_output)

    stop_testing_server(server)
    dns_repeater.stop()

    save_results(request_trees[key], key, request_trees[key].get_root().get_resource(),\
                     blocked_total, blocked_not_transitive, blocked_fp_attempts)
    
    # Start the evaluation...

    _ = input("Press a key to exit...\n")

def save_results(tree: dict, filename: str, pagename: str, blocked_total: int, \
                 blocked_not_transitive: int, blocked_fp_attempts: int) -> None:
    """Function to save results for a given page to a file"""

    # Try creating results folder if it doesnt exist
    if not os.path.exists(RESULTS_FOLDER):
        print("Creating the results folder...")
        os.makedirs(RESULTS_FOLDER)

    tree_image = tree.print_tree()

    result_dict = {"page":pagename, "blocked_resources_total": blocked_total,\
                    "blocked_resources_without_transitivity": blocked_not_transitive,\
                    "blocked_fp_attempts":blocked_fp_attempts}
    result_file_path = RESULTS_FOLDER + filename
    tree_file = RESULTS_FOLDER + filename.split('.')[0] + "_tree" + ".json"

    with open(result_file_path, 'w', encoding='utf-8') as f:
        jsoned_traffic = json.dumps(result_dict, indent=4)
        f.write(jsoned_traffic)
        f.close()

    with open(tree_file, 'w', encoding='utf-8') as f:
        f.write(tree_image)
        f.close()


if __name__ == "__main__":
    start()
