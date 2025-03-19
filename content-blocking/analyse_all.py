import os
import subprocess
from time import sleep

from source.file_manipulation import load_json, save_json
from source.constants import RESULTS_FOLDER, EXPERIMENT_NAME, BROWSER_TYPE


options = load_json("./config.json")
log_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith("_log.json")]

command = ["python", "./start.py", "--analysis-only"]

len_to_remove = len("_log.json")
for file in log_files:
    file_len = len(file)
    remove_index = file_len - len_to_remove
    experiment_name = file[:remove_index]

    options[EXPERIMENT_NAME] = experiment_name
    if experiment_name.startswith("firefox"):
        options[BROWSER_TYPE] = "firefox"
    else:
        options[BROWSER_TYPE] = "chrome"

    save_json(options, "./config.json")
    sleep(1)

    process = subprocess.Popen(command, shell=True)

    sleep(1)
