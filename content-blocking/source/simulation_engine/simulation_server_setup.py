# test_page_server.py
# Serves HTML web-page that fetches the observedd resources
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

# Function which takes the request tree.
# Based on the request tree, obtain all resources.
# Create HTML page that uses javascript to fetch all the resources

# Default modules
from multiprocessing import Process

# 3rd-party modules
from flask import Flask, render_template

# server app global variable
app = Flask(__name__, template_folder="simulation_webserver")

list_of_resources = []

@app.route('/')
def index() -> str:
    """Function to return an index page for the test server.
    
    Returns:
        str: Rendered HTML document of the page
    """
    if not list_of_resources:
        print("Could not load any resources! Is traffic folder empty?")
    return render_template("index.html", resources=list_of_resources,\
                            n_of_resources=len(list_of_resources))

def run_test_server(resource_list: list) -> None:
    """Function to launch the test server with the configured resources
    
    Args:
        resource_list: List of all resources from all loaded trees
    """
    global list_of_resources
    list_of_resources = resource_list

    # http://localhost:5000
    app.run(port=5000, use_reloader=False)

def start_testing_server(resource_list: list) -> Process:
    """Function to start the http testing server to observe content blocking behavior
    
    Args:
        resource_list: List of all resources from all loaded trees

    Returns:
        Process: The process which runs the server
    """
    print("Starting the test server...")

    # Start another process running the server
    server = Process(target=run_test_server, args=(resource_list, ))
    server.start()
    return server

def stop_testing_server(server: Process) -> None:
    """Function to stop the given http testing server

    Args:
        server: The process which runs the server.
    """
    print("Stopping the test server...")
    server.terminate()
    server.join()
