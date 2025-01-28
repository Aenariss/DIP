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

# My modules
from source.constants import TRAFFIC_FOLDER, GENERAL_ERROR
from source.load_traffic import load_traffic

parser = argparse.ArgumentParser(prog="Content-blocking evaluation",
                                 description="Evaluates given content-blocking\
                                      tools on given pages")
parser.add_argument('-l', '--load', action="store_true",
                    help="Whether to observe network traffic anew using page_list.txt")
args = parser.parse_args()

def start() -> None:
    """Main driver function"""
    # If load was specified, go through the specified pages and observe traffic
    if args.load:
        # (Re)create the traffic folder
        if not os.path.exists(TRAFFIC_FOLDER):
            os.makedirs(TRAFFIC_FOLDER)
        # Delete existing logs if the folder exists
        else:
            for file in os.listdir(TRAFFIC_FOLDER):
                filename = TRAFFIC_FOLDER + file
                if os.path.isfile(filename):
                    os.remove(filename)

        load_traffic()
        print("Traffic observation finished!")

    # Check that the traffic folder exists
    if not os.path.exists(TRAFFIC_FOLDER):
        print("Couldn't find the folder with the observed traffic!\n" +
              "Run the program with '--load' argument first!")
        exit(GENERAL_ERROR)
    else:
        # If the traffic folder is empty, it needs to be loaded
        if len([file for file in os.listdir(TRAFFIC_FOLDER)
                if os.path.isfile(TRAFFIC_FOLDER + file)]) == 0:
            print("Couldn't find the folder with the observed traffic!\n" +
                "Did you specify at least 1 page in the page_list.txt file? " +
                "If so, run the program with '--load' argument first!")
            exit(GENERAL_ERROR)

    # Start the evaluation...

start()
