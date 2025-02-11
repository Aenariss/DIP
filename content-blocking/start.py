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
from time import sleep

# Custom modules
from source.constants import TRAFFIC_FOLDER, GENERAL_ERROR, OPTIONS_FILE
from source.load_traffic import load_traffic
from source.request_tree import create_trees
from source.test_page_server import start_testing_server, stop_testing_server
from source.dns_repeater import DNSRepeater


parser = argparse.ArgumentParser(prog="Content-blocking evaluation",
                                 description="Evaluates given content-blocking\
                                      tools on given pages")
parser.add_argument('-l', '--load', action="store_true",
                    help="Whether to observe network traffic anew using page_list.txt")
args = parser.parse_args()

def start() -> None:
    """Main driver function"""

    # Load options for the evaluation
    if not os.path.exists(OPTIONS_FILE):
        print("Could not load ``options.json`` file!")

    with open(OPTIONS_FILE, encoding="utf-8") as f:
        options = json.load(f)

    # If load was specified, go through the specified pages and observe traffic
    if args.load:
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

        print("Loading the traffic...")
        load_traffic(options)
        print("Traffic loading finished!")

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

    request_trees = create_trees()

    # For each loaded page, create a testing server and visit it
    for (key, _) in request_trees.items():
        
        # Start the testing server as another process for each logged page traffic
        server = start_testing_server(request_trees[key].get_all_requests())

        # Setup DNS resolving so that the same IPs as observed are used
        dns_repeater = DNSRepeater(key)
        dns_repeater.start()

        sleep(20)
        #test_server_visit()

        dns_repeater.stop()
        stop_testing_server(server)

    # Start the evaluation...

    # For each fetch, replay dns response
    # Add mechanism for adding multiple extensions and browsers and repeat for each

if __name__ == "__main__":
    start()

# tbd: run multiple instances in parallel to speed-up data collection
