# load_page_file.py
# Loads all pages specified in pageList.txt and returns them as an array.
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

# Custom modules
from source.constants import FILE_ERROR

def load_pages() -> list[str]:
    """Function to load the page_list.txt file and return its content"""
    try:
        with open("page_list.txt", 'r', encoding='utf-8') as f:
            # strip newline characters at the end of each line
            return [line[:-1] for line in f.readlines()]
    except OSError:
        print("Error reading the content of page_list.txt! Is the file present?")
        exit(FILE_ERROR)
