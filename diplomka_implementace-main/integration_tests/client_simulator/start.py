#
#  Copyright (C) 2019  Amit Datta
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

import sys
import json
from start_visit.start_pet import test_pet 
import concurrent.futures

'''
Start the visits in parallel.

    exp : str
        Name of the experiment.
    browsers : [str]
        Browsers to be tested this run.
    pets : [str]
        Extensions to be tested this run.
    server_config : JSON object
        Configuration of the run.
    delay : int
        Duration of page visit in seconds.
'''
def start_native_threaded(exp, browsers, pets, server_config, delay):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for browser in browsers:
                test_pet(exp, browser, pets[browser][0], server_config, delay)
                for pet in pets[browser][1:]:
                    futures.append(
                        executor.submit(test_pet, exp, browser, pet, server_config, delay)
                )
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Thread error: {e}")

'''
Start the visits sequentially. Intended for obsevation and interaction.

    exp : str
        Name of the experiment.
    browsers : [str]
        Browsers to be tested this run.
    pets : [str]
        Extensions to be tested this run.
    server_config : JSON object
        Configuration of the run.
    delay : int
        Duration of page visit in seconds.
'''
def start_native_interactive(exp, browsers, pets, server_config, delay):
            for browser in browsers:
                for pet in pets[browser]:
                    test_pet(exp, browser, pet, server_config, delay)          


'''
Read client configuration data
    data : JSON object
        Client configuration from JSON file.
    
    -----------------------------------------
    
    exp : str
        Name of the experiment.
    browsers : [str]
        Browsers to be tested this run.
    pets : [str]
        Extensions to be tested this run.
    server_config : JSON object
        Configuration of the run.
    delay : int
        Duration of page visit in seconds

'''
def get_experiment_attributes(data):
    exp = data["experiment_name"]
    browsers = data["browsers"]
    pets = data["pets"]
    delay = data["delay"]
    mode = data["mode"]

    return exp, browsers, pets, delay, mode

if __name__ == '__main__':
    if(len(sys.argv) != 3):
        print("Call as follows: python3 start.py experiment_config_file server_config_file")
        sys.exit(0)

    experiment_config = sys.argv[1]
    with open(experiment_config) as f:
        data = json.load(f)
        exp, browsers, pets, delay, mode = get_experiment_attributes(data)

    server_config = sys.argv[2]

    if mode == "threaded":
        try:
            print("Starting the visits in threaded mode.")
            start_native_threaded(exp, browsers, pets, server_config, delay)
        except:
            print("Please give valid json files as input. See vm_all.json and vm_server.json as the template.")
            sys.exit(0)
    elif mode == "interactive":
        try:
            print("Starting the visits in interactive mode.")
            start_native_interactive(exp, browsers, pets, server_config, delay)
        except:
            print("Please give valid json files as input. See vm_all.json and vm_server.json as the template.")
            sys.exit(0)
    else:
        print("Please supply correct JSON congfiguration files.")
        sys.exit(0)


