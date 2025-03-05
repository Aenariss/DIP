# constants.py
# Specifies constants and user-defined options
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
ADDON_FOLDER = "./addons/"
FPD_GROUP_FOLDER = "./source/fp_files/"
CHROME_ADDONS_FOLDER = ADDON_FOLDER + "chrome/"
FIREFOX_ADDONS_FOLDER = ADDON_FOLDER + "firefox/"

# Paths - files
PAGES_FILE = "page_list.txt"
USER_CONFIG_FILE = "./config.json"
FPD_GROUPS_FILE = FPD_GROUP_FOLDER + "groups.json"
FPD_WRAPPERS_FILE = FPD_GROUP_FOLDER + "wrappers.json"

JSHELTER_FPD_PATH = CHROME_ADDONS_FOLDER + "jshelter_0_19_custom_fpd.crx"

# Paths - system
HOSTS_FILE = "C:/Windows/System32/drivers/etc/hosts"

# User option strings from config.json
PAGE_WAIT_TIME = "page_wait_time"
BROWSER_TYPE = "browser_type"
BROWSER_VERSION = "browser_version"
USING_CUSTOM_BROWSER = "using_custom_browser"
CUSTOM_BROWSER_BINARY = "custom_browser_binary"
TESTED_ADDONS = "tested_addons"
EXPERIMENT_NAME = "experiment_name"
LOGGING_BROWSER_VERSION = "logging_browser_version"
TIME_UNTIL_TIMEOUT = "time_until_timeout"

# DNS server docker container name
DNS_CONTAINER_NAME = "bind9"
DNS_CONTAINER_IMAGE = "internetsystemsconsortium/bind9:9.20"
