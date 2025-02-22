# load_traffic.py
# Observe traffic on given pages and save it into a file.
# Also observe the corresponding DNS responses.
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
import os
import re

# Custom modules
from source.file_loading import load_pages
from source.page_http_traffic import get_page_traffic
from source.constants import TRAFFIC_FOLDER, FILE_ERROR, GENERAL_ERROR
from source.dns_observer import DNSSniffer

def load_traffic(options: dict, compact: bool) -> None:
    """Function to observe traffic on given list of pages"""
    print("Loading the traffic...")

    pages = load_pages()

    # Counter to name files like 1.json, 2.json... to prevent issues
    filename_counter = 1

    # Go through each page and observe traffic
    for page in pages:

        sniffer = DNSSniffer()
        sniffer.start_sniffer()

        # Get the HTTP(S) traffic associated with a page
        try:
            traffic = get_page_traffic(page, options, compact)
            if traffic == {}:
                sniffer.stop_sniffer()
                filename_counter += 1
                continue
        except Exception:
            # Page may not load correctly - skip it and continue
            sniffer.stop_sniffer()
            continue

        sniffer.stop_sniffer()
        dns_traffic = sniffer.get_traffic()

        save_traffic(dns_traffic, page, str(filename_counter), "dns")
        save_traffic(traffic, page, str(filename_counter), "http")
        match_jshelter_fpd(filename_counter)
        filename_counter += 1

    print("Traffic loading finished!")

def save_traffic(traffic: dict, pagename: str, filename: str, traffic_type: str) -> None:
    """Function to append observed traffic to the traffic file"""
    try:
        f = None
        if traffic_type == "dns":
            f = open(TRAFFIC_FOLDER + filename + '_dns' + '.json', 'w', encoding='utf-8')
        else: # http
            f = open(TRAFFIC_FOLDER + filename + '_network.json', 'w', encoding='utf-8')
        # Format the dictionary as json
        jsoned_traffic = json.dumps(traffic, indent=4)
        f.write(jsoned_traffic)
        f.close()

    except OSError as error:
        print("Could not save traffic to a file! Problem with page:", pagename)
        print(error)
        exit(FILE_ERROR)

def match_jshelter_fpd(filename: int) -> None:
    """Function to match the downloaded JSHelter FPD report file to its results"""

    # Since JShelter exports name of the page, it will be the only file in traffic folder
    # with different name compared to the others. 

    # Load the only different file and rename it to match the others
    files = [f for f in os.listdir(TRAFFIC_FOLDER) if not re.match(r'^[0-9]', f)]

    # There should be 2 non-matching files -> .empty and fpd file, find the fpd file
    # However, sometimes, the download may trigger twice -> delete other non-matching
    found_files = []
    for file in files:
        if file != ".empty":
            found_files.append(file)

    if not found_files:
        print("Can't match FP file to its corresponding traffic files!")
        print("Did you put something in ./traffic/ folder? Or visited bad page...")
        exit(GENERAL_ERROR)

    original_filepath = TRAFFIC_FOLDER + found_files[0]
    new_filename = TRAFFIC_FOLDER + str(filename) + "_fp.json"
    os.rename(original_filepath, new_filename)

    # Remove original renamed file so that it is not deleted
    found_files.remove(found_files[0])

    # Delete other found files
    for file in found_files:
        os.remove(TRAFFIC_FOLDER + file)
