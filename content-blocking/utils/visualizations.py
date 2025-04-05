# visualizations.py
# Simple module to create visualizations. Not part of the evaluation.
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
import sys

# 3rd-party modules
from tabulate import tabulate

# Add the parent directory (root folder) to sys path to allow
# running as python ./utils/analyse_all.py
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_directory)

# Custom modules
from source.file_manipulation import load_json

FOLDER_WITH_RESULTS = "./results/upper_bound/"
RESULT_FILES = [f for f in os.listdir(FOLDER_WITH_RESULTS) if (f != ".empty" and not\
                f.startswith("chrome_browser") and not f.startswith("firefox_pure"))]
CHROME_RESULTS = [f for f in RESULT_FILES if not f.startswith("firefox")]
FIREFOX_RESULTS = [f for f in RESULT_FILES if f.startswith("firefox")]
SUM = "sum"
AVERAGE = "average"

def result_dict(result_files):
    """Function to create dict with the results"""

    all_results = {}

    # For each result file load its results
    for result_file in result_files:

        res_len = len("_results")
        experiment_name = os.path.splitext(result_file)[0]
        experiment_name = experiment_name[0:len(experiment_name) - res_len]
        experiment_name = experiment_name.split("_")

        experiment_name = [word.capitalize() for word in experiment_name if not word.isnumeric()]
        experiment_name = [word[0].lower() + word[1].upper() + word[2:] if\
                            word.startswith("Ublock") else word for word in experiment_name]
        experiment_name = ' '.join(experiment_name)

        experiment_results = load_json(FOLDER_WITH_RESULTS + result_file)
        all_results[experiment_name] = experiment_results

    return all_results


def obtain_results_of_metric(results_for_tools: dict, metric: str, result_type: str):
    """Function to obtain desired results of a given type (sum/average/n_of_results)"""
    sub_results_of_type = {}

    if metric.startswith("average"): # Average block level
        result_type = AVERAGE
    # Each result has Browser, results scheme
    for (experiment, results) in results_for_tools.items():
        try:
            sub_results_of_type[experiment] = results[metric][result_type]
        except Exception:
            print("Your specified metric or result type does not exist!")
            exit(0)

    return sub_results_of_type

def print_table(results_for_tools, metrics, submetrics, headers):
    """Prints a formatted table instead of a graph."""

    all_metric_values = {}
    for metric in metrics:
        metric_values = obtain_results_of_metric(results_for_tools, metric, SUM)

        for (tool, value) in metric_values.items():
            # Nested values
            if isinstance(value, dict):
                if all_metric_values.get(tool):
                    for submetric in submetrics:
                        all_metric_values[tool].append(value[submetric])
                else:
                    all_metric_values[tool] = []
                    for submetric in submetrics:
                        all_metric_values[tool].append(value[submetric])
            else:
                if all_metric_values.get(tool):
                    all_metric_values[tool].append(value)
                else:
                    all_metric_values[tool] = [value]

    table_data = []

    # Order in which I want to print the results
    # corresponds to the structure I have in tables in latex
    desired_order = ['Avast Secure Browser', 'Brave Browser', 'Firefox Browser',\
                    'Chrome Adblock Plus', 'Firefox Adblock Plus', 'Chrome Ghostery',\
                    'Firefox Ghostery', 'Chrome Privacy Badger', 'Firefox Privacy Badger',\
                    'Chrome uBlock Origin Lite', 'Firefox uBlock Origin']

    all_metric_values = {key: all_metric_values[key] for key in desired_order}

    # If the result has subresults (subtrees, fpd...)
    # print result for all given subresults
    # else just format the number
    for (tool, values) in all_metric_values.items():
        if isinstance(values, dict):
            row = [tool] + [values.get(x, 0) for x in headers[1:]]
        else:
            row = [tool]
            for val in values:
                formatted_number = f"{val:,.3f}".replace(',', ' ').rstrip('0').rstrip('.')
                row.append(formatted_number)

        table_data.append(row)

    print(r"\begin{table}[H]")
    print(r"\centering")
    print(tabulate(table_data, headers=headers, tablefmt="latex"))
    print(r"\caption{Table to test captions and labels.}")
    print(r"\label{table:1}")
    print(r"\end{table}")

def main():
    """Main function to print tables
    
    Change the code using the defined metrics according to what you want to print
    """
    results_for_tools = result_dict(RESULT_FILES)
    fpd_metrics = [
        "fpd_attempts_blocked_directly", "fpd_attempts_blocked_transitively", 
        "fpd_attempts_blocked_in_total"]
    fpd_submetrics = ["BrowserProperties", "AlgorithmicMethods", "CrawlFpInspector"]

    request_metrics = ["requests_blocked_directly", "requests_blocked_transitively",\
                       "requests_blocked_in_total"]

    experimental_metrics = ["requests_blocked_that_have_child_requests",\
                            "average_request_block_level"]

    subtree_data = ["blocked_subtrees_data"]
    subtree_submetrics = ["subtrees_fully_blocked", "subtrees_partially_blocked",\
                          "subtrees_not_blocked"]
    root_node_submetric = ["trees_with_blocked_root_node"]

    metrics = request_metrics
    headers = ["Tool", "1", "2", "3"]
    submetrics = root_node_submetric

    print_table(results_for_tools, metrics, submetrics, headers)

if __name__ == "__main__":
    main()
