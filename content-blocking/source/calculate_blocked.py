# calculate_blocked.py
# Functions to calculate how many requests (& fp attemtps) in the request chain were blocked.
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

# Local modules
from source.request_tree import RequestTree

def calculate_blocked(request_tree: RequestTree, console_output: list[dict]) -> tuple[int, int, int]:
    """Function to calculate how many requests in a tree would be blocked 
    if given resources were blocked and how many fp attempts that would prevent"""

    print("Calculating number of blocked requests and fingerprinting attempts...")

    # Obtain URLs of resources that were blocked by client
    client_blocked_pages = parse_console_logs(console_output)

    # Calculate number of blocked requests and blocked fp attempts
    blocked_pages_transitively, blocked_pages, blocked_fp_attempts = request_tree.calculate_blocked(client_blocked_pages)

    print("Finished calculation!")

    return blocked_pages_transitively, blocked_pages, blocked_fp_attempts

def parse_console_logs(console_output: list[dict]) -> list[str]:

    # Works for chrome - check it works for firefox!
    blocked_by_client_error = "ERR_BLOCKED_BY_CLIENT"
    error_length = len(blocked_by_client_error)

    blocked_pages = []

    for report in console_output:
        # Only do anything if it was an error
        if report["level"] == "SEVERE":
            message = report["message"]

            # Obtain the last part of the string w/ the error
            try:
                last_part = message[-error_length:]

                # It was blocked by client
                if last_part == blocked_by_client_error:

                    # get the url of the resource - split by space and the first is url
                    parts_of_message = message.split(' ')
                    url = parts_of_message[0]
                    blocked_pages.append(url)

            # If obtaining was impossible, it was not an error
            except Exception:
                continue

    return blocked_pages
