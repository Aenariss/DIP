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
from source.constants import GENERAL_ERROR
from source.file_loading import load_json, get_traffic_files

ANONYMOUS_CALLER = "<anonymous>"

def parse_fp() -> dict:
    """Function to load FP attempts from a corresponding file and
    assign each domain a nuimber of observed attempts.
    
    Returns assigned fp attempts to each site for each fp log
    """

    # Get FP files from traffic folder
    print("Assigning FP attempts to each site...")

    fp_files = get_traffic_files('fp')

    fp_attempts = {}

    for file in fp_files:
        pure_filename = os.path.basename(file)
        corresponding_network_file = get_network_file(pure_filename)

        fp_data = load_json(file)

        fp_attempts[corresponding_network_file] = get_fp_attempts(fp_data)

    print("Finished assigning FP attempts to each site!")
    return fp_attempts

def get_network_file(file: str) -> str:
    """Function to obtain name of corresponding network file from other traffic file"""
    def handle_file_error(arr: list) -> None:
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


def get_fp_attempts(fp_data: dict) -> dict:
    """Function to get FP attempts from given FP file and return number address and its attempts"""

    fp_logs = {}

    # Go through the log file and obtain access logs
    try:
        for (log_key, _) in fp_data.items():
            access_logs = fp_data[log_key]

            # Go through each logged site in the report
            for (site_key, _) in access_logs.items():
                site_data = access_logs[site_key]

                # Go through each FP property
                for (_, fp_property_logs) in site_data.items():
                    fp_logs = parse_property_logs(fp_property_logs, fp_logs)

    except Exception as e:
        print(e)
        print("Could not load FP attempts from a FP logfile!")
        exit(GENERAL_ERROR)

    return fp_logs

def parse_property_logs(property_logs: dict, fp_logs: dict) -> dict:
    """Function to parse fingerprinting property data from the logs"""

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
                fp_logs[ANONYMOUS_CALLER] += total
            else:
                fp_logs[ANONYMOUS_CALLER] = total

        # The caller will be only the last page which actually called the resource
        # Similar to the request tree, where predecessor is the last page in callstack
        fp_logs = parse_callers(callers, fp_logs)

    return fp_logs

def parse_callers(all_callers: dict, fp_logs: dict) -> dict:
    """Function to parse callstack of a property"""
    def parse_last_caller(last_caller: str) -> str:
        """Inline method to parse last caller string to obtain only the URL"""

        # Split it by space and get the last
        split_by_space = last_caller.split(" ")
        last_caller = split_by_space[-1]

        # Remove brackets in case they're there
        if (last_caller[0]) == '(':
            last_caller = last_caller[1:-1]

        # Split twice from the right, because last caller has formatting :1:1 (line number)
        last_caller = last_caller.rsplit(':', 2)

        last_caller = last_caller[0]

        return last_caller

    # Callstacks are still in the form of a key in dict, obtain it
    # Get all callers of a given property
    for (callers, _) in all_callers.items():

        # Split the callstack by a newline
        callstack = callers.split("\n")

        # Get the last caller
        last_caller = parse_last_caller(callstack[-1])

        # Each callstack means one more attempt, add it to the page attempts count
        current_page_total = fp_logs.get(last_caller)

        # Page was not logged yet
        if not current_page_total:
            fp_logs[last_caller] = 1

        # Page has already been observedd to attempt some FP
        else:
            fp_logs[last_caller] = current_page_total + 1

    return fp_logs
