# traffic_loader.py
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
from source.file_manipulation import load_pages
from source.traffic_logger.network_logs_loader import get_page_network_traffic
from source.constants import TRAFFIC_FOLDER, FILE_ERROR, GENERAL_ERROR
from source.traffic_logger.dns_observer import DNSSniffer
from config import Config

def get_address(resource: str) -> str:
    """Function to obtain only the domain from URL
    Needs for the URL to end with '/', logs from Chrome logging fit this form
    
    Args:
        resource: URL of the resource
        
    Returns:
        domain (str): URL of the domain, if available
    """
    domain = ""
    matched = re.search(r"\/\/(.*?)\/", resource)
    if matched:
        domain = matched.group(1)

    return domain

def is_dns_valid(dns_traffic: dict, network_traffic: list) -> tuple[bool, dict]:
    """Function to ensure all observed network resources have also its DNS logged
    Also removes unnecessary DNS records of primary domains (not subdomains)
    that do not match any of the network requests
    
    Args:
        dns_traffic: Logged DNS traffic
        network_traffic: Logged network traffic

    Returns:
        tuple:
            - status (bool): If the logged DNS contains reply for all observed network resources
            - observed_dns_logs (dict): DNS traffic with removed unrelated DNS replies
    """

    status = False
    observed_dns_logs = {}

    # Mark all DNS logs as unnecessary in the beginning
    for (key, _) in dns_traffic.items():
        observed_dns_logs[key] = False

    # Go through all network traffic and check the domain is in the DNS logs
    for resource in network_traffic:
        requested_resource = resource["requested_resource"]

        # skip all data:, blob: etc
        if not requested_resource.startswith("http"):
            continue

        address = get_address(requested_resource)

        # If empty address was returned, nothing was matched meaning an error
        if address == "":
            print(f"Invalid domain obtained for {requested_resource}!")
            print("CDP format could have changed! Or just some strange address...")
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

    # Go through all DNS and delete all records that do not belong to logged network request.
    for (key, subdomains) in observed_dns_logs.items():
        if not observed_dns_logs[key]:
            del dns_traffic[key]

    # Check each logged DNS reply contains valid answer
    for (_, subdomains) in dns_traffic.items():
        # For each valid key, check all subkeys are either CNAMEs or A, both cant be empty
        for (_, records) in subdomains.items():
            cname_records = records.get("CNAME", [])
            a_records = records.get("A", [])

            if not a_records and not cname_records:
                return status, {}

    status = True

    return status, dns_traffic

def visit_page(page: str, options: Config, compact: bool) -> tuple[bool, list]:
    """Function to visit the specified page and obtain its network traffic
    
        Args:
            page: URL of the page to visit
            options: Instance of Config
            compact: Whether to save only the final valid caller in call stacks to save space
        
        Returns:
            tuple:
                - status (bool): Whether the page visit (and log obtaining) was successful
                - network_traffic (list): Logged network events 
    """
    network_traffic = []
    status = True
    try:
        # Get the network traffic associated with a page
        network_traffic = get_page_network_traffic(page, options, compact)
        if not network_traffic:
            status = False
    except Exception:
        # Page may not load correctly - skip it and continue
        status = False

    return status, network_traffic

def save_traffic(traffic: dict, pagename: str, filename: str, traffic_type: str) -> None:
    """Function to save observed traffic as a file
    
    Args:
        traffic: Traffic that should be saved (either DNS or Network)
        pagename: Name of the page from which the traffic was collected
        filename: Number of the accessed page as a str (1,2...)
        traffic_type: Type of saved traffic ('dns' or 'network')
    """
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

    except Exception as e:
        print("Could not save traffic to a file! Problem with page:", pagename)
        print(e)
        delete_unsuccesfull_fpd()
        exit(FILE_ERROR)

def delete_unsuccesfull_fpd() -> None:
    """Function to delete FPD files for pages that failed to correctly load"""

    # Load the only different files (Downloaded FPD file name not matching the log format)
    files = [f for f in os.listdir(TRAFFIC_FOLDER) if not re.match(r'^[0-9]', f)]

    # if it wasnt .empty, load them and delete them
    for file in files:
        if file != ".empty":
            os.remove(TRAFFIC_FOLDER + file)

def match_jshelter_fpd(current_log_number: int) -> None:
    """Function to match the downloaded JSHelter FPD report file to its results
    
    Args:
        current_log_number: Number of the currently visited page (e.g. 5), since
        logs are stored in format 5_{network|dns|fpd}.json...
    """

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
    new_filename = TRAFFIC_FOLDER + str(current_log_number) + "_fp.json"
    os.rename(original_filepath, new_filename)

    delete_unsuccesfull_fpd()


def get_page_logs(sniffer: DNSSniffer, page: str, options: Config, compact: bool)\
      -> tuple[dict, list]:
    """Function to obtain network and dns logs from a carried out page visit
    
        Args:
            sniffer: Instance of a DNSSniffer
            page: URL of the page from which to obtain logs
            options: Instance of Config
            compact: Whether to save only the final valid caller in call stacks to save space

        Returns:
            tuple:
                - dict: DNS traffic logged from the visited page
                - list: Network traffic obtained from the visited page
    """
    sniffer.start_sniffer()

    # Get the HTTP(S) traffic associated with a page
    visit_status, network_traffic = visit_page(page, options, compact)

    # If error, return nothing
    if not visit_status:
        sniffer.stop_sniffer()
        return {}, []

    sniffer.stop_sniffer()
    dns_traffic = sniffer.get_traffic()

    return dns_traffic, network_traffic

def load_traffic(options: Config, compact: bool) -> None:
    """Function to observe traffic on given list of pages. 
    Saves the observed traffic into ./traffic/ folder.

    Args:
        options: Instance of Config with valid settings
        compact: Whether to log only the final valid caller instead of the entire call stack
    """
    print("Loading the traffic...")

    pages = load_pages()

    # Counter to name files like 1.json, 2.json... to prevent issues
    filename_counter = 1
    max_file_counter = len(pages)
    max_attempts = options.max_repeat_log_attempts

    # Go through each page and observe traffic
    for page in pages:

        attempts = 0

        # A new instance needs to be created for each page since the sniffer saves logged packets
        # reusing it would keep the previous packets
        sniffer = DNSSniffer()

        print(f"Page visit progress: {filename_counter}/{max_file_counter}")
        dns_traffic, network_traffic = get_page_logs(sniffer, page, options, compact)

        # If no DNS validation, it is always valid
        if options.no_dns_validation_during_logging:
            dns_validity = True
        else:
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
                dns_traffic, network_traffic = get_page_logs(sniffer, page, options, compact)
                dns_validity, dns_traffic = is_dns_valid(dns_traffic, network_traffic)
            else:
                break

            # If network error happened that did not happen before, try again
            if not network_traffic:
                print(f"Error loading {page}! Trying again...")
                dns_validity = False

        if not dns_validity:
            print(f"Could not correctly sniff DNS traffic for {page}! Skipping...")
            filename_counter += 1
            delete_unsuccesfull_fpd()
            continue

        # Save the results and match downloaded JShelter report to the current result
        save_traffic(dns_traffic, page, str(filename_counter), "dns")
        save_traffic(network_traffic, page, str(filename_counter), "http")
        match_jshelter_fpd(filename_counter)
        filename_counter += 1

    print("Traffic loading finished!")
