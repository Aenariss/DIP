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

# Custom modules
from source.file_loading import load_pages
from source.page_http_traffic import get_page_traffic
from source.constants import TRAFFIC_FOLDER, FILE_ERROR
from source.dns_observer import DNSSniffer

def load_traffic(options: dict) -> None:
    """Function to observe traffic on given list of pages"""
    pages = load_pages()

    # Counter to name files like 1.json, 2.json... to prevent issues
    filename_counter = 1

    # Go through each page and observe traffic
    for page in pages:

        sniffer = DNSSniffer()
        sniffer.start_sniffer()

        # Get the HTTP(S) traffic associated with a page
        traffic = get_page_traffic(page, options)

        sniffer.stop_sniffer()
        dns_traffic = sniffer.get_traffic()

        save_traffic(dns_traffic, page, str(filename_counter), "dns")
        save_traffic(traffic, page, str(filename_counter), "http")
        filename_counter += 1

def save_traffic(traffic: dict, pagename: str, filename: str, traffic_type: str) -> None:
    """Function to append observed traffic to the traffic file"""
    try:
        f = None
        if traffic_type == "dns":
            f = open(TRAFFIC_FOLDER + filename + '_dns' + '.json', 'w', encoding='utf-8')
        else:
            f = open(TRAFFIC_FOLDER + filename + '.json', 'w', encoding='utf-8')
        # Format the dictionary as json
        jsoned_traffic = json.dumps(traffic, indent=4)
        f.write(jsoned_traffic)
        f.close()

    except OSError as error:
        print("Could not save traffic to a file! Problem with page:", pagename)
        print(error)
        exit(FILE_ERROR)
