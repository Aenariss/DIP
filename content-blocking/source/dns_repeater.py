# dns_repeater.py
# Edits the /etc/hosts file so that the observed IP addresses are used for DNS answers
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

# Default modules
import json

# Custom modules
from source.constants import HOSTS_FILE, GENERAL_ERROR, TRAFFIC_FOLDER

class DNSRepeater:
    """Class representing the object used to manipulate hosts file"""
    def __init__(self, filekey: str, hosts_file: str=None) -> None:
        """Method to initialize the object. Loads the DNS data 
        from the name of the corresponding traffic file"""
        self.filekey = filekey

        # If the host file was defined, use it
        self.hosts_file = hosts_file

        self.original_hosts_file_content = None

        # If not, use the default windows path
        if not hosts_file:
            self.hosts_file = HOSTS_FILE

        self.__load_hosts_file()

    def get_hosts_file(self) -> str:
        """Method to return path to the hosts file"""
        return self.hosts_file

    def get_original_hosts_file_content(self) -> str:
        """Method to return original content of the hsots file"""
        return self.original_hosts_file_content

    def __load_hosts_file(self) -> None:
        """Internal method to load content of the original hosts file"""
        with open(self.get_hosts_file(), 'r', encoding='utf-8') as f:
            content = f.read()
            self.original_hosts_file_content = content

    def get_filekey(self) -> str:
        """Method to return the filekey representing the file with HTTP traffic"""
        return self.filekey

    def __appent_to_hosts(self) -> str:
        """Method to append custom addresses to the content of the hostfile
           Returns string with the new content to be put into the file"""

        # Get name of the file with corresponding parsed results
        corresponding_file = self.get_filekey().split('.')

        # Handle the results file was correct
        if len(corresponding_file) != 2:
            print("Could not load corresponding DNS traffic for the file", self.get_filekey())
            exit(GENERAL_ERROR)

        # dns file is results_file + _dns.json
        dns_filepath = TRAFFIC_FOLDER + corresponding_file[0] + "_dns.json"

        content_to_append = ""

        try:
            # Open the DNS file
            with open(dns_filepath, 'r', encoding='utf-8') as f:
                dns_replies = json.load(f)

                # Iterate over all queried domains
                for (domain, _) in dns_replies.items():

                    # Each domain may have multiple query results,
                    # use only the first one (the rest should be cached)
                    replies = dns_replies[domain]

                    # No result for given query, should not happen
                    if len(replies) < 1:
                        print("Corrupted DNS file content! Launch again with ``--load`` argument")
                        exit(GENERAL_ERROR)

                    first_reply = replies[0]

                    # Iterate over all IP addresses and add them to the hosts file
                    # in the same order DNS returned them the first time
                    for ip_address in first_reply:
                        content_to_append += "\n"
                        content_to_append += ip_address + ' ' + domain

        except Exception as e:
            print(e)
            print("Could not open corresponding DNS file! Trying to open:", dns_filepath)
            exit(GENERAL_ERROR)

        original_content = self.get_original_hosts_file_content()
        new_content = original_content + '\n' + content_to_append
        return new_content

    def start(self) -> None:
        """Method to populate the hosts file with the logged DNS responses"""
        try:
            with open(self.get_hosts_file(), 'w', encoding='utf-8') as f:
                f.write(self.__appent_to_hosts())
        except Exception as e:
            self.__show_exception_and_quit(e)

    def stop(self) -> None:
        """Method to stop repeating DNS responses -> Return the hosts file to the original state"""
        try:
            with open(self.get_hosts_file(), 'w', encoding='utf-8') as f:
                f.write(self.get_original_hosts_file_content())
        except Exception as e:
            self.__show_exception_and_quit(e)

    def __show_exception_and_quit(self, e: Exception) -> None:
        """Internal method to handle errors"""
        print(e)
        print("Error opening HOSTS file! Check you're running the program" +
              "as an admin -> refer to README.md")
        exit(GENERAL_ERROR)
