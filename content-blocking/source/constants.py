# constants.py
# Specifies constants
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

# Errors
GENERAL_ERROR = 1
FILE_ERROR = 51

# Paths - folders
TRAFFIC_FOLDER = "./traffic/"
RESULTS_FOLDER = "./results/"
DNS_CONFIGURATION_FOLDER = "./custom_dns_server/server_configuration/"

# Paths - files
PAGES_FILE = "page_list.txt"
OPTIONS_FILE = "config.json"

# Paths - system
HOSTS_FILE = "C:/Windows/System32/drivers/etc/hosts"

# User option strings from options.json
PAGE_WAIT_TIME = "page_wait_time"

# DNS server docker container name
DNS_CONTAINER_NAME = "bind9"
DNS_CONTAINER_IMAGE = "internetsystemsconsortium/bind9:9.20"
