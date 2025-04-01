# file_manipulation.py
# Provides function for data loading such as from page_list.txt
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
from source.constants import FILE_ERROR, TRAFFIC_FOLDER, GENERAL_ERROR

def load_pages() -> list[str]:
    """Function to load the page_list.txt file and return its content
    
    Returns:
        list[str]: List of pages from page_file.txt
    """
    try:
        with open("page_list.txt", 'r', encoding='utf-8') as f:
            # strip newline characters at the end of each line
            return [line[:-1] if line[-1] == '\n' else line for line in f.readlines()]
    except OSError:
        print("Error reading the content of page_list.txt! Is the file present?")
        exit(FILE_ERROR)

def load_json(path: str) -> dict:
    """Function to load a given JSON file and return its content as dict
    
    Args:
        path: Path to the loaded json

    Returns:
        dict: Content of the loaded json
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except OSError:
        print("Error reading the content of " + path + "! Is the file present?")
        exit(FILE_ERROR)

def save_json(json_file, path) -> None:
    """Function to save a given JSON file
    
    Args:
        json_file: Content of the JSON to save
        path: Where to save the file
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json_file, f, ensure_ascii=False, indent=4)
    except OSError:
        print("Error saving json into " + path + "!")
        exit(FILE_ERROR)

def get_traffic_files(traffic_type: str) -> list:
    """Function to obtain filenames for given type of file from the ./traffic/ folder

    Args:
        traffic_type: Type of traffic to get - 'dns', 'fp', 'network'
    
    Returns:
        list: List of files matching the given filter
    """

    # Types of traffic files to ignore
    inverse_regex = [r"fp", r"dns", r"network"]

    if traffic_type in inverse_regex:
        # Remove given type of files from the inverse regex to obtain them
        inverse_regex.remove(traffic_type)
    else:
        print("Invalid traffic file type!")
        exit(GENERAL_ERROR)

    # Append .empty file to not count it
    inverse_regex.append(r"\.empty")

    # Create the regex by adding '|' between the options
    inverse_regex = '|'.join(inverse_regex)

    # Load the only the type of file we want from the traffic folder
    files = [TRAFFIC_FOLDER + f for f in os.listdir(TRAFFIC_FOLDER)
            if not re.search(inverse_regex, f)]

    return files
