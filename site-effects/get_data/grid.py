#
#  JShelter is a browser extension which increases level
#  of security, anonymity and privacy of the user while browsing the
#  internet.
#
#  Copyright (C) 2020  Martin Bednar
#  Copyright (C) 2024  Jana Petranova
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import subprocess
from time import sleep

from configuration import Config


## Start Selenium Grid server as a new process on background.
def start_server():
    start_server_command = ['java', '-jar', Config.selenium_server_jar_path, 'hub']
    server = subprocess.Popen(start_server_command)
    sleep(6)
    return server


## Start Selenium Grid Nodes as a new processes.
def start_nodes():
    nodes = []
    if Config.number_of_grid_nodes_on_this_device == 0:
        # Waiting on distributed environment when all Selenium Grid nodes will be running.
        input("When all testing nodes will be running, press Enter to start system testing.")
    else:
        for node_number in range(Config.number_of_grid_nodes_on_this_device):
            print("Adding node")
            nodes.append(subprocess.Popen(["java", "-jar", Config.selenium_server_jar_path, "node", "--hub", "http://" + Config.grid_server_ip_address + ":4444/grid/register/", "--selenium-manager", "true"], text=True))
            sleep(7)
    return nodes


## End nodes when testing is finished.
def end_nodes(nodes, manually):
    if manually:
        input("After testing, press Enter to end the nodes.")
    for node in nodes:
        node.kill()


## End Selenium Grid server when testing is finished and all nodes are terminated.
def end_server(server):
    server.kill()
