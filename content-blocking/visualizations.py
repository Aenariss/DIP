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

# 3rd-party modules
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import LogLocator, FuncFormatter
from tabulate import tabulate

# Custom modules
from source.file_manipulation import load_json

FOLDER_WITH_RESULTS = "./results/upper_bound/"
RESULT_FILES = [f for f in os.listdir(FOLDER_WITH_RESULTS) if (f != ".empty" and not f.startswith("chrome_browser"))]
CHROME_RESULTS = [f for f in RESULT_FILES if not f.startswith("firefox")]
FIREFOX_RESULTS = [f for f in RESULT_FILES if f.startswith("firefox")]
SUM = "sum"
AVERAGE = "average"

def plot_results(results, metric, metric_legend, value_in_bar, legend, output_file):
    """Generates a grouped bar chart with a log-scaled y-axis and saves it as a PDF."""
    
    # Extract data directly into lists
    tools = []
    values = []
    labels = []  # Corresponding metric labels

    metric_values = obtain_results_of_metric(results, metric, SUM)

    for tool, nested_values in metric_values.items():
        if isinstance(nested_values, dict):  # If metric has sub-categories
            for method, value in nested_values.items():
                tools.append(tool)
                values.append(value)
                labels.append(method)
        elif isinstance(nested_values, (int, float)):
            tools.append(tool)
            values.append(nested_values)
            labels.append(metric_legend)

    # Create the bar plot
    plt.figure(figsize=(14, 10))
    ax = sns.barplot(x=tools, y=values, hue=labels, palette="tab10")

    # Set log scale for y-axis
    plt.yscale('log')

    # Format y-axis ticks to display regular numbers (1000 instead of 10^3)
    def custom_log_formatter(x, pos):
        return f'{int(x):,}'  # Format as integer with thousands separator

    plt.gca().yaxis.set_major_locator(LogLocator(base=10, subs=(1, 3, 7), numticks=6))
    plt.tick_params(axis='y', labelsize=18)  
    plt.gca().yaxis.set_major_formatter(FuncFormatter(custom_log_formatter))

    if value_in_bar:
        # **Add value labels inside bars**
        for p in ax.patches:
            height = p.get_height()
            if height > 0:  # Avoid placing text on zero-height bars
                ax.text(
                    x=p.get_x() + p.get_width() / 2,  # Center horizontally
                    y=height * 0.9,  # Position inside the bar (90% of the height)
                    s=f"{int(height):,}",  # Format with thousands separator
                    ha="center", va="top", color="white", fontsize=8, fontweight="bold"
                )

    # Formatting
    plt.xticks(rotation=45, ha="right", fontsize=18)
    plt.ylabel(metric_legend, fontsize=18)
    plt.title(f"{metric_legend}", fontsize=18)
    if legend:
        plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    else:
        ax.legend_.remove()
    plt.tight_layout()

    # Save the figure as a vector-based PDF
    plt.savefig(output_file, format="pdf")
    plt.show()

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
        experiment_name = [word[0].lower() + word[1].upper() + word[2:] if word.startswith("Ublock")\
                            else word for word in experiment_name]
        experiment_name = ' '.join(experiment_name)

        experiment_results = load_json(FOLDER_WITH_RESULTS + result_file)
        all_results[experiment_name] = experiment_results

    return all_results


def obtain_results_of_metric(results: dict, metric: str, result_type: str):
    """Function to obtain desired results of a given type (sum/average/n_of_results)"""
    sub_results_of_type = {}

    if metric.startswith("average"): # Average block level
        result_type = AVERAGE
    for (experiment, results) in results.items():
        try:
            sub_results_of_type[experiment] = results[metric][result_type]
        except Exception:
            print("Your specified metric or result type does not exist!")
            exit(0)

    return sub_results_of_type

def print_table(results, metrics, submetrics, headers, total, percentage):
    """Prints a formatted table instead of a graph."""

    all_metric_values = {}
    for metric in metrics:
        metric_values = obtain_results_of_metric(results, metric, SUM)

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

    for (tool, values) in all_metric_values.items():
        if isinstance(values, dict):
            row = [tool] + [values.get(x, 0) for x in headers[1:]]
        else:
            row = [tool]
            for val in values:
                formatted_number = f"{val:,.3f}".replace(',', ' ').rstrip('0').rstrip('.')
                row.append(formatted_number)
                if percentage:
                    row.append(str("%.2f" % (val/total) * 100) + ' %')

        table_data.append(row)

    print(r"\begin{table}[H]")
    print(r"\centering")
    print(tabulate(table_data, headers=headers, tablefmt="latex"))
    print(r"\caption{Table to test captions and labels.}")
    print(r"\label{table:1}")
    print(r"\end{table}")

def main():

    results = result_dict(RESULT_FILES)
    fpd_metrics = [
        "fpd_attempts_blocked_directly", "fpd_attempts_blocked_transitively", 
        "fpd_attempts_blocked_in_total", "fpd_attempts_observed"]
    
    request_metrics = ["requests_blocked_directly", "requests_observed", 
        "requests_blocked_in_total", "requests_blocked_transitively"]
    
    experimental_metrics = ["requests_blocked_that_have_child_requests", "average_request_block_level"]

    metric = "fpd_attempts_blocked_directly"
    metric_legend = "FPD Attempts Blocked Directly"
    value_in_bar = True
    legend = True

    #plot_results(results, metric, metric_legend, value_in_bar, legend, "requests_blocked_directly.pdf")

    metrics = ["requests_blocked_directly", "requests_observed", 
        "requests_blocked_in_total"]
    headers = ["Tool", "RBCR", "ARBL"]
    submetrics = ["BrowserProperties", "AlgorithmicMethods", "CrawlFpInspector"]

    first_key = list(results.keys())[0]
    total = results[first_key]["requests_observed"][SUM]
    percentage = False
    print_table(results, metrics, submetrics, headers, total, percentage)
    


if __name__ == "__main__":
    main()