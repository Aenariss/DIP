# analyse_all.py
# Very simple script to run --analysis-only for all logs in the results/ folder

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
import os
import subprocess
from time import sleep

# Custom modules
from source.file_manipulation import load_json, save_json
from source.constants import RESULTS_FOLDER, EXPERIMENT_NAME, BROWSER_TYPE

def run_analyses():
    options = load_json("./config.json")
    log_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith("_log.json")]

    # Command to be used for all launches
    launch_command = ["python", "./start.py", "--analysis-only"]

    # Remove this part from each _log file
    len_to_remove = len("_log.json")

    for file in log_files:
        file_len = len(file)
        remove_index = file_len - len_to_remove

        # Compute experiment_name for each logs
        experiment_name = file[:remove_index]

        # Edit config accordingly to allow correct log parsing for each simulation result
        options[EXPERIMENT_NAME] = experiment_name
        if experiment_name.startswith("firefox"):
            options[BROWSER_TYPE] = "firefox"
        else:
            options[BROWSER_TYPE] = "chrome"

        save_json(options, "./config.json")
        sleep(1)

        # Launch each analysis as a new subprocess
        subprocess.Popen(launch_command, shell=True)

        sleep(1)

if __name__ == "__main__":
    run_analyses()
