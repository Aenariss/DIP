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
import time

# Custom modules
from source.file_manipulation import load_pages
from source.page_http_traffic import get_page_traffic
from source.constants import TRAFFIC_FOLDER, FILE_ERROR, GENERAL_ERROR, MAX_LOG_ATTEMPTS
from source.dns_observer import DNSSniffer

def load_traffic(options: dict, compact: bool) -> None:
    """Function to observe traffic on given list of pages"""
    print("Loading the traffic...")

    pages = load_pages()

    # Counter to name files like 1.json, 2.json... to prevent issues
    filename_counter = 1
    max_file_counter = len(pages)

    max_attempts = options.get(MAX_LOG_ATTEMPTS)

    # Go through each page and observe traffic
    for page in pages:

        attempts = 1
        sniffer = DNSSniffer()

        print(f"Page visit progress: {filename_counter}/{max_file_counter}")
        dns_traffic, network_traffic = get_page_logs(sniffer, page, options, compact)

        dns_validity, dns_traffic = is_dns_valid(dns_traffic, network_traffic)

        if not network_traffic:
            print(f"Error loading {page}! Skipping...")
            delete_unsuccesfull_fpd()
            filename_counter += 1
            continue

        # Check all traffic has its DNS logged
        # If DNS error, try again as many times as user wants
        while attempts < max_attempts:
            attempts += 1
            if not dns_validity:

                print(f"Could not correctly sniff DNS traffic for {page}! Trying again...")
                delete_unsuccesfull_fpd()
                # Give it some time
                time.sleep(6)
                dns_traffic, network_traffic = get_page_logs(sniffer, page, options, compact)
                dns_validity, dns_traffic = is_dns_valid(dns_traffic, network_traffic)
            else:
                break

            # If not network error happened that did not happen before, try again
            if not network_traffic:
                print(f"Error loading {page}! Trying again...")
                dns_validity = False

        if not dns_validity:
            print(f"Could not correctly sniff DNS traffic for {page}! Skipping...")
            filename_counter += 1
            delete_unsuccesfull_fpd()
            continue

        save_traffic(dns_traffic, page, str(filename_counter), "dns")
        save_traffic(network_traffic, page, str(filename_counter), "http")
        match_jshelter_fpd(filename_counter)
        filename_counter += 1

    print("Traffic loading finished!")

def get_page_logs(sniffer: DNSSniffer, page: str, options: dict, compact: bool)\
      -> tuple[dict, list]:

    sniffer.start_sniffer()

    # Get the HTTP(S) traffic associated with a page
    visit_status, network_traffic = visit_page(page, options, compact)

    # If error, skip the page
    if not visit_status:
        sniffer.stop_sniffer()
        return {}, []

    # Give sniffer time to process all callbacks
    time.sleep(1)
    sniffer.stop_sniffer()

    time.sleep(1)
    dns_traffic = sniffer.get_traffic()

    return dns_traffic, network_traffic


def visit_page(page: str, options: dict, compact: bool) -> tuple[bool, list]:
    # Get the HTTP(S) traffic associated with a page
    network_traffic = []
    try:
        network_traffic = get_page_traffic(page, options, compact)
        if not network_traffic:
            return False, network_traffic
        return True, network_traffic
    except Exception:
        # Page may not load correctly - skip it and continue
        return False, network_traffic

def get_address(resource: str) -> str:
    """Function to obtain only the page address from URL"""
    matched = re.search(r"\/\/(.*?)\/", resource)
    if matched:
        return matched.group(1)

    return ""

def is_dns_valid(dns_traffic: dict, network_traffic: list) -> tuple[bool, dict]:
    """Function to ensure all observed network resources have also its DNS logged
    Also removes unnecessary DNS records that do not match any of the network requests"""

    status = False
    observed_dns_logs = {}

    # Mark all DNS logs as unnecessary in the beginning
    for (key, _) in dns_traffic.items():
        observed_dns_logs[key] = False

    for resource in network_traffic:
        requested_resource = resource["requested_resource"]

        # skip all data:, blob: etc
        if not requested_resource.startswith("http"):
            continue

        address = get_address(requested_resource)

        # If empty address was returned, nothing was matched meaning an error
        if address == "":
            print("CDP format has probably changed! Fix load_traffic.py")
            return status, {}

        split = address.split('.')
        last_two = split[-2:]
        rest = split[:-2]

        # In case the page was like google.com, meaning no subdomains, use it all to check
        if not rest:
            rest = last_two

        top_level_key = '.'.join(last_two)
        top_level = dns_traffic.get(top_level_key, None)

        if not top_level:
            return status, {}

        subdomain = top_level.get('.'.join(rest), None)
        if not subdomain:
            return status, {}

        # Set the page as necessary
        observed_dns_logs[top_level_key] = True

        # Set all logged CNAMEs for this domain as neccessary
        for (_, records) in dns_traffic[top_level_key].items():
            cname_records = records.get("CNAME", [])
            for record in cname_records:
                split = record.split('.')
                last_two = split[-2:]
                cname_key = '.'.join(last_two)
                observed_dns_logs[cname_key] = True

    # Go through all DNS and delete all records that do not belong to network request.
    for (key, subdomains) in observed_dns_logs.items():
        if not observed_dns_logs[key]:
            # Check it's not a CNAME-only record
            del dns_traffic[key]

    for (_, subdomains) in dns_traffic.items():
        # For each valid key, check all subkeys are either CNAMEs or A, both cant be empty
        for (_, records) in subdomains.items():
            cname_records = records.get("CNAME", [])
            a_records = records.get("A", [])

            if not a_records and not cname_records:
                return status, {}

    status = True

    return status, dns_traffic

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

def delete_unsuccesfull_fpd() -> None:
    """Funciton to delete FPD files for pages that failed to correctly load"""

    # Load the only different files
    files = [f for f in os.listdir(TRAFFIC_FOLDER) if not re.match(r'^[0-9]', f)]

    # if it wasnt .empty, load them and delete them
    for file in files:
        if file != ".empty":
            os.remove(TRAFFIC_FOLDER + file)

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
        _, extension = os.path.splitext(file)
        if file != ".empty":
            # Only add JSON files
            if extension == ".json":
                found_files.append(file)

    if not found_files:
        print("Can't match FP file to its corresponding traffic files!")
        print("Did you put something in ./traffic/ folder? Or visited bad page...")
        exit(GENERAL_ERROR)

    original_filepath = TRAFFIC_FOLDER + found_files[0]
    new_filename = TRAFFIC_FOLDER + str(filename) + "_fp.json"
    os.rename(original_filepath, new_filename)

    delete_unsuccesfull_fpd()
