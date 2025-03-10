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

# Custom modules
from source.constants import TRAFFIC_FOLDER, GENERAL_ERROR, RESULTS_FOLDER, USER_CONFIG_FILE
from source.constants import PAGE_WAIT_TIME, BROWSER_TYPE, USING_CUSTOM_BROWSER, TESTED_ADDONS
from source.constants import BROWSER_VERSION, EXPERIMENT_NAME, LOGGING_BROWSER_VERSION
from source.constants import CUSTOM_BROWSER_BINARY
from source.load_traffic import load_traffic
from source.fp_attempts import parse_fp
from source.request_tree import create_trees
from source.test_page_server import start_testing_server, stop_testing_server
from source.file_manipulation import save_json, load_json
from source.visit_test_server import visit_test_server
from source.analysis import analyse_trees
from source.firewall import firewall_unblock_traffic
from source.utils import squash_dns_records, squash_tree_resources

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
parser.add_argument('-ao', '--analysis-only', action="store_true",
        help="Whether to use skip using local server to calculate blocked requests and use logs")
parser.add_argument('-so', '--simulation-only', action="store_true",
        help="Whether to use only perform simulation using local server")
parser.add_argument('-tso', '--testing-server-only', action="store_true",
        help="Whether to only start a testing server and do nothing else")
args = parser.parse_args()

def valid_options(options: dict) -> bool:
    """Function to check if given user configuration is valid"""
    browser_type = options.get(BROWSER_TYPE)
    page_wait_time = options.get(PAGE_WAIT_TIME)
    custom_browser = options.get(USING_CUSTOM_BROWSER)
    browser_version = options.get(BROWSER_VERSION)
    tested_addons = options.get(TESTED_ADDONS)
    experiment_name = options.get(EXPERIMENT_NAME)
    logging_browser_version = options.get(LOGGING_BROWSER_VERSION)
    custom_browser_binary = options.get(CUSTOM_BROWSER_BINARY, "")

    result = [True]

    # The fields need to be present
    if not browser_version or not experiment_name or not logging_browser_version\
        or custom_browser is None or tested_addons is None:
        result.append(False)

    # Browser type supported is only chrome and firefox
    if browser_type not in ["chrome", "firefox"]:
        result.append(False)

    # Page wait time must be a valid number
    if not str(page_wait_time).isnumeric():
        result.append(False)

    # Custom browser specifies whether something else chromium or firefox-based is used
    # Can only be 1 or 0
    if custom_browser not in [0,1]:
        result.append(False)

    # If custom browser is being used, check binary is not empty
    if custom_browser == 1:
        if custom_browser_binary == "":
            result.append(False)

    # If at least one setting was false, return False
    return all(result)

def initialize_folders() -> dict:
    """Function to prepare folderes to be used during evaluation. Returns user options."""

    # Load options for the evaluation
    options = load_json(USER_CONFIG_FILE)

    if not valid_options(options):
        print("Invalid config.json content!")
        print("Consult README.md for proper configuration setting")
        exit(GENERAL_ERROR)

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

def obtain_data(options: dict) -> bool:
    """Function to load traffic and save it in traffic folder"""
    # Check user arguments were correct
    if args.load:
        if args.load_only:
            print("You can only use one argument! Either '--load' or '--load-only'!")
            exit(GENERAL_ERROR)

    # If load or load-only was specified, go through the specified pages and observe traffic
    if args.load or args.load_only:
        load_traffic(options, args.compact)

        # if load-only was specified, don't do anything else and quit
        if args.load_only:
            return True
    return False

def parse_traffic() -> dict:
    """Function to parse the traffic logs and return request trees"""
    # Check traffic folder is present and not empty
    check_traffic_folder()

    # Assign total FP attempts for each domain from FP logs
    fp_attempts = parse_fp()

    # Create initiator tree-like chains from data in the ./traffic/ folder
    request_trees = create_trees(fp_attempts)

    return request_trees

def obtain_simulation_results(request_trees: dict, options: dict) -> list[dict]:
    """Function to simulate what would happen had the tool been present during the visits.

    Creates a test server with all the logged resources and visits it to measure how many
    will a tool block. 

    Loads up custom DNS server running in docker. Temporarily changes network settings.
    
    Saves the result into results/experiment_name. In case results for this experiment are already
    present (running an analysis on previously obtained results), loads it. Returns the result."""

    def save_console_log(console_output, experiment_name) -> None:
        """Function to save the console logs into results/ folder"""
        if not os.path.exists(RESULTS_FOLDER):
            print("Creating the results folder...")
            os.makedirs(RESULTS_FOLDER)
        save_json(console_output, RESULTS_FOLDER + experiment_name + ".json")

    console_output = None

    # Only do this if --analysis-only was not specified.
    if not args.analysis_only:

        # Squash DNS records and contacted pages from all observations together
        dns_records = squash_dns_records()
        resource_list = squash_tree_resources(request_trees)


        print(len(resource_list))

        # Start the DNS server and set it as prefered to repeat responses
        dns_repeater = DNSRepeater(dns_records)

        # Start the testing server as another process for each logged page traffic
        server = start_testing_server(resource_list)

        try:
            # Visit the server and log the console outputs
            console_output = visit_test_server(options, resource_list, dns_repeater, args, server)

            save_console_log(console_output, options.get(EXPERIMENT_NAME) + "_log")
        except Exception as e:
            print(e)
            print("Error while simulating data!")
            exit(GENERAL_ERROR)
        finally:
            stop_testing_server(server)
            firewall_unblock_traffic()
            dns_repeater.stop()

    # In case --simulation-only was specified, stop here
    if args.simulation_only:
        return console_output

    # In case --analysis-only was specified, load the saved output.
    if not console_output:
        console_output = load_json(RESULTS_FOLDER + options.get(EXPERIMENT_NAME) + "_log.json")

    return console_output

def analyze_results(request_trees: dict, console_output: list[dict], options: dict) -> None:
    """Function to analyze logged request trees based on obtained console output, logging
    the results into a file in ./results/ folder."""

    results = analyse_trees(request_trees, console_output, options)
    save_json(results, RESULTS_FOLDER + options.get(EXPERIMENT_NAME) + "_results.json")

def start() -> None:
    """Main driver function"""

    # Load user options
    options = initialize_folders()

    # Generate traffic
    obtain_only = obtain_data(options)
    if obtain_only:
        return

    # Generate request trees from traffic data
    request_trees = parse_traffic()

    print(f"Starting experiment {options.get(EXPERIMENT_NAME)}...")

    # Obtain console output of experiment
    console_output = obtain_simulation_results(request_trees, options)

    print("Experiment data succesfully loaded...")

    if args.simulation_only:
        return

    # Analyze what would have happened to the request tree had a content-blocking tool been present
    analyze_results(request_trees, console_output, options)

    print(f"Finished experiment {options.get(EXPERIMENT_NAME)}...")

if __name__ == "__main__":
    start()
