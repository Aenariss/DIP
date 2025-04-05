# analyse_all.py
# Very simple helper script to run --analysis-only for all logs in the results/ folder

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
from multiprocessing import Process
from time import sleep
import sys

# Add the parent directory (root folder) to sys path to allow
# running as python ./utils/analyse_all.py
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_directory)

# Custom modules
from source.constants import RESULTS_FOLDER
from config import Config
from start import start

def run_analyses():
    log_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith("_log.json")]

    # Remove this part from each _log file
    len_to_remove = len("_log.json")
    processes = []

    for file in log_files:
        file_len = len(file)
        remove_index = file_len - len_to_remove

        # Compute experiment_name for each logs
        experiment_name = file[:remove_index]

        current_config = Config()

        # Edit config accordingly to allow correct log parsing for each simulation result
        current_config.experiment_name = experiment_name
        if experiment_name.startswith("firefox"):
            current_config.browser_type = "firefox"
        else:
            current_config.browser_type = "chrome"

        sleep(1)

        # Launch each analysis as a new subprocess
        proc = Process(target=start, args=(current_config, True))
        proc.start()
        processes.append(proc)

        sleep(1)

    # Optional: Wait for all subprocesses to finish
    for proc in processes:
        proc.join()

if __name__ == "__main__":
    run_analyses()
