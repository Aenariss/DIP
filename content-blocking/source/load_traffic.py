# load_traffic.py
# Observe traffic on given pages and save it into a file.
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
from source.load_page_file import load_pages
from source.page_traffic import get_page_traffic
from source.constants import TRAFFIC_FOLDER, FILE_ERROR

def load_traffic(options: dict) -> None:
    """Function to observe traffic on given list of pages"""
    pages = load_pages()

    # Counter to name files like 1.json, 2.json... to prevent issues
    filename_counter = 1

    # Go through each page and observe traffic
    for page in pages:
        traffic = get_page_traffic(page, options)
        save_traffic(traffic, page, str(filename_counter))
        filename_counter += 1

def save_traffic(traffic: dict, pagename: str, filename: str) -> None:
    """Function to append observed traffic to the traffic file"""
    try:
        with open(TRAFFIC_FOLDER + filename + '.json', 'w', encoding='utf-8') as f:
            # Format the dictionary as json
            jsoned_traffic = json.dumps(traffic, indent=4)
            f.write(jsoned_traffic)
            f.close()
    except OSError as error:
        print("Could not save traffic to a file! Problem with page:", pagename)
        print(error)
        exit(FILE_ERROR)
