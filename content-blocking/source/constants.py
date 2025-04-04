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
DNS_CONFIGURATION_FOLDER = "./source/simulation_engine/custom_dns_server/server_configuration/"
ADDON_FOLDER = "./addons/"
FPD_GROUP_FOLDER = "./source/traffic_parser/fp_files/"
CHROME_ADDONS_FOLDER = ADDON_FOLDER + "chrome/"
FIREFOX_ADDONS_FOLDER = ADDON_FOLDER + "firefox/"

# Paths - files
PAGES_FILE = "page_list.txt"
USER_CONFIG_FILE = "./config.json"
FPD_GROUPS_FILE = FPD_GROUP_FOLDER + "groups.json"
FPD_WRAPPERS_FILE = FPD_GROUP_FOLDER + "wrappers.json"
NAMED_CONF_FILE = DNS_CONFIGURATION_FOLDER + "named.conf"

JSHELTER_FPD_PATH = CHROME_ADDONS_FOLDER + "jshelter_0_19_custom_fpd.crx"
FIREFOX_RESOURCE_LOGGER = FIREFOX_ADDONS_FOLDER + "firefox_resource_logger.xpi"

# Paths - system
HOSTS_FILE = "C:/Windows/System32/drivers/etc/hosts"

# DNS server docker container name
DNS_CONTAINER_NAME = "bind9"
DNS_CONTAINER_IMAGE = "internetsystemsconsortium/bind9:9.20"
