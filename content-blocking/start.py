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
import time
import sys

# Custom modules
from source.constants import TRAFFIC_FOLDER, GENERAL_ERROR, RESULTS_FOLDER
from source.traffic_logger.traffic_loader import load_traffic
from source.traffic_parser.fp_attempts import parse_fp
from source.traffic_parser.create_request_trees import create_trees
from source.simulation_engine.simulation_server_setup import start_testing_server
from source.simulation_engine.simulation_server_setup import stop_testing_server
from source.file_manipulation import save_json, load_json
from source.simulation_engine.visit_test_server import visit_test_server
from source.analysis_engine.analysis import analyse_trees
from source.simulation_engine.firewall import firewall_unblock_traffic, firewall_block_traffic
from source.utils import squash_dns_records, squash_tree_resources
from source.config import Config
from source.simulation_engine.custom_dns_server.dns_repeater_server import DNSRepeater

# Increase recursion limit because of the trees, should be more than enough
sys.setrecursionlimit(3000)

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
        help="Whether to only perform simulation using local server without analysis")
parser.add_argument('-tso', '--testing-server-only', action="store_true",
        help="Whether to only start a testing server and do nothing else")
parser.add_argument('-eb', '--early-blocking', action="store_true",
        help="Whether to setup firewall and DNS settings before driver setup")
args = parser.parse_args()

def initialize_folders():
    """Function to prepare folderes to be used during evaluation"""

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

def obtain_data(options: Config) -> bool:
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

def parse_traffic(options: Config) -> dict:
    """Function to parse the traffic logs and return request trees"""
    # Check traffic folder is present and not empty
    check_traffic_folder()

    # Assign total FP attempts for each domain from FP logs
    fp_attempts = parse_fp()

    valid_fp_attempts = 0
    for (_, value) in fp_attempts.items():
        if value != {}:
            valid_fp_attempts += 1

    print(f"FP Attempts succesfully collected for {valid_fp_attempts}\
out of {len(fp_attempts.items())} logs.")


    # Create initiator tree-like chains from data in the ./traffic/ folder
    request_trees = create_trees(fp_attempts, options)

    return request_trees

def obtain_simulation_results(request_trees: dict, options: Config) -> list[dict]:
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

    # Squash DNS records and contacted pages from all observations together
    dns_records = squash_dns_records()
    resource_list = squash_tree_resources(request_trees)

    # Only do this if --analysis-only was not specified.
    if not args.analysis_only:

        # Start the DNS server and set it as prefered to repeat responses
        dns_repeater = DNSRepeater(dns_records)

        # Start the testing server as another process for each logged page traffic
        server = start_testing_server(resource_list)

        try:
            if args.early_blocking:
                dns_repeater.start()
                firewall_block_traffic()
                time.sleep(3)

            # Visit the server and log the console outputs
            console_output = visit_test_server(options, resource_list, dns_repeater, args)

            save_console_log(console_output, options.experiment_name + "_log")
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
        console_output = load_json(RESULTS_FOLDER + options.experiment_name + "_log.json")

    return console_output

def analyze_results(request_trees: dict, console_output: list[dict], options: Config) -> None:
    """Function to analyze logged request trees based on obtained console output, logging
    the results into a file in ./results/ folder."""

    results = analyse_trees(request_trees, console_output, options)
    save_json(results, RESULTS_FOLDER + options.experiment_name + "_results.json")

def start(options: Config=None, analysis_only: bool=False) -> None:
    """Main driver function"""

    # Initialize folder structure
    initialize_folders()

    # Manually set analysis_only to work with analyse_all
    if analysis_only:
        args.analysis_only = analysis_only

    # Load config only if none was provided
    if not options:
        options = Config()

    # Validate options
    status = options.validate_settings()

    if not status:
        print("Invalid Configuration! Consult the original file!")
        exit(1)

    # Generate traffic
    obtain_only = obtain_data(options)
    if obtain_only:
        return

    # Generate request trees from traffic data
    request_trees = parse_traffic(options)

    print(f"Starting experiment {options.experiment_name}...")

    # Obtain console output of experiment
    console_output = obtain_simulation_results(request_trees, options)

    print("Experiment data succesfully loaded...")

    if args.simulation_only:
        input("Press any key to exit...")
        return

    # Analyze what would have happened to the request tree had a content-blocking tool been present
    analyze_results(request_trees, console_output, options)

    print(f"Finished experiment {options.experiment_name}...")

if __name__ == "__main__":
    start()
