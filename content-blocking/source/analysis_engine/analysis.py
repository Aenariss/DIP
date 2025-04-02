# analysis.py
# Analyses request trees and simulates blocking based on simulation results
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

# Custom modules
from config import Config
from source.traffic_parser.request_tree import RequestTree
from source.utils import print_progress, add_substract_fp_attempts
from source.constants import GENERAL_ERROR

from source.analysis_engine.experimental_analysis import add_subtrees, analyse_subtrees_blocking
from source.analysis_engine.experimental_analysis import calculate_blocked_who_brings_children
from source.analysis_engine.experimental_analysis import calculate_average_block_level
from source.analysis_engine.requests_analysis import calculate_total_blocked_requests
from source.analysis_engine.requests_analysis import calculate_really_blocked_requests
from source.analysis_engine.fingerprinting_analysis import calculate_directly_blocked_fpd_attempts
from source.analysis_engine.fingerprinting_analysis import calculate_total_blocked_fpd_attempts
from source.analysis_engine.fingerprinting_analysis import calculate_total_fpd_attempts
from source.analysis_engine.analysis_utils import get_directly_blocked_tree
from source.analysis_engine.analysis_utils import get_transitively_blocked_tree
from source.analysis_engine.analysis_utils import process_firefox_console_output
from source.analysis_engine.analysis_utils import parse_console_logs_chrome


def simulate_blocking(request_tree: RequestTree, blocked_resources: list[str]) -> dict:
    """Defines and computes various data about each page with simulated content-blocking
    tool present. Assumes the requested resources would have been the same with the 
    content-blockin tool present.

    Args:
        request_tree: Original request tree representing page structure
        blocked_resources: List of resources given tool would have blocked
    
    Returns:
        dict: Calculated metrics for a given page
    """

    # Get number of total resources
    total_requested = len(request_tree.get_all_requests())
    total_fpd_attempts = calculate_total_fpd_attempts(request_tree)

    # Project the resource blocking into trees
    directly_blocked_tree = get_directly_blocked_tree(request_tree, blocked_resources)
    transitively_blocked_tree = get_transitively_blocked_tree(request_tree, blocked_resources)

    # Calculate request blocking
    total_blocked = calculate_total_blocked_requests(transitively_blocked_tree)
    really_blocked_nodes = calculate_really_blocked_requests(directly_blocked_tree)
    directly_blocked = len(really_blocked_nodes)
    blocked_transitively = total_blocked - directly_blocked

    # Calculate fp blocking
    direct_fpd_blocked = calculate_directly_blocked_fpd_attempts(directly_blocked_tree)
    total_fpd_blocked = calculate_total_blocked_fpd_attempts(transitively_blocked_tree)
    transitive_fpd_blocked = add_substract_fp_attempts(total_fpd_blocked, direct_fpd_blocked,\
                                                        add=False)

    # Calculate experimental metrics
    blocked_subtrees_data = analyse_subtrees_blocking(directly_blocked_tree)
    average_block_level = calculate_average_block_level(directly_blocked_tree)
    blocked_with_children = calculate_blocked_who_brings_children(really_blocked_nodes)

    return {
        # Total FPD attempts observed
        "fpd_attempts_observed": total_fpd_attempts,
        # Number of FPD attempts blocked directly
        "fpd_attempts_blocked_directly": direct_fpd_blocked,
        # Number of FPD attempts blocked transitively
        "fpd_attempts_blocked_transitively": transitive_fpd_blocked,
        # Total number of FPD attempts blocked
        "fpd_attempts_blocked_in_total": total_fpd_blocked,
        # Number of all rsources requested
        "requests_observed": total_requested,
        # Number of resources blocked directly
        "requests_blocked_directly": directly_blocked,
        # Number of all resources blocked (even transtiviely)
        "requests_blocked_in_total": total_blocked,
        # Number of resources blocked transitively
        "requests_blocked_transitively": blocked_transitively,
        # N of blocked resources which brought kids
        "requests_blocked_that_have_child_requests": blocked_with_children,
        # Average level at which resource was blocked
        "average_request_block_level": average_block_level,
        # N of fully/partially/not blocked subtrees
        "blocked_subtrees_data": blocked_subtrees_data
    }

def compute_sums_count_resources(results: list[dict], total_results: dict) -> dict:
    """Function to calculate "sum" and "n_of_results" attributes for partial results
    
    Args:
        results: Partial results for each request tree
        total_results: Dict to which the partial results are summarized

    Returns:
        dict: Updated total_results
    """
    # Go through all partial results
    for result in results:

        # For each result, go through each sub-result
        for (sub_result, total_result) in total_results.items():

            # Check if its not fpd - we need to be special for that
            if "fpd" in sub_result:
                total_result["sum"] = add_substract_fp_attempts(total_result["sum"],\
                                                                result[sub_result])
            # Subtrees are special case since they use dicts but are not FPD
            elif sub_result == "blocked_subtrees_data":
                total_result["sum"] = add_subtrees(total_result["sum"], result[sub_result])
            else:
                # For average block level, do not increase N of results if no blocking occured
                if sub_result == "average_request_block_level":
                    if result[sub_result] == 0:
                        total_result["n_of_results"] -= 1
                total_result["sum"] += result[sub_result]

            # increase number of results by one for each record
            total_result["n_of_results"] += 1

    return total_results

def compute_averages(total_results: dict) -> dict:
    """Function to calculate "average" attributes from partial results
    
    Args:
        total_results: Dict to which the averages are computed.
                       Needs to already contain computed "sum" and "n_of_results" attributes.

    Returns:
        dict: Updated total_results
    """
    # Each result has sum value stored in together with nubmer of results - calculate averages
    for (sub_result, total_result) in total_results.items():

        # If its FPD stat, I need to approach it by calculating each FP sub-attribute
        if "fpd" in sub_result or sub_result == "blocked_subtrees_data":

            # Create deep copy of sum to divide by n_of_results
            total_result["average"] = dict(total_result["sum"])
            for (group_name, count) in total_result["average"].items():
                total_result["average"][group_name] = count / total_result["n_of_results"]

        else:
            # For average block level, check there was at least 1, else set this metric to 0
            if sub_result == "average_request_block_level":
                if total_result["n_of_results"] > 0:
                    total_result["average"] = total_result["sum"] / total_result["n_of_results"]
                else:
                    total_result["average"] = 0
            else:
                total_result["average"] = total_result["sum"] / total_result["n_of_results"]

    return total_results

def parse_partial_results(results: list[dict]) -> dict:
    """Calculates finished results from a collection of partial results by
    computing the sum and/or average of each value
    
    Args:
        results: List of results computed for each page

    Returns:
        dict: Results spanning the entire dataset in a single dict
    """

    sub_result = {
        "n_of_results": 0,
        "sum": 0,
        "average": 0
    }

    sub_result_dicts = {
        "n_of_results": 0,
        "sum": {},
        "average": {}
    }

    # Initialize completed results, needs to use same keys as in simulate_blocking() function
    total_results = {
        "fpd_attempts_observed": dict(sub_result_dicts),
        "fpd_attempts_blocked_directly": dict(sub_result_dicts),
        "fpd_attempts_blocked_transitively": dict(sub_result_dicts),
        "fpd_attempts_blocked_in_total": dict(sub_result_dicts),
        "requests_observed": dict(sub_result),
        "requests_blocked_directly": dict(sub_result),
        "requests_blocked_in_total": dict(sub_result),
        "requests_blocked_transitively": dict(sub_result),
        "requests_blocked_that_have_child_requests": dict(sub_result),
        "average_request_block_level": dict(sub_result),
        "blocked_subtrees_data": dict(sub_result_dicts)
    }

    total_results = compute_sums_count_resources(results, total_results)
    total_results = compute_averages(total_results)

    return total_results

def analyze_tree(request_tree: RequestTree, client_blocked_pages: list) -> dict:
    """Function to calculate how many requests in a tree would be blocked 
    if given resources were blocked and how many fp attempts that would prevent
    
    Args:
        request_tree: Request tree representing page structure
        client_blocked_pages: List of pages blocked by a given tool

    Returns:
        dict: Computed metrics for the given request tree
    """

    # Calculate what would have happened hat the content blocking tool been present
    results = simulate_blocking(request_tree, client_blocked_pages)

    return results

def analyze_trees(request_trees: dict, console_output: list, options: Config) -> dict:
    """Function to launch analysis on each tree and calculate average values 
    of each observed property
    
    Args:
        request_trees: All request trees representing visited pages
        console_output: Output from the simulation, both Chrome and Firefox
        options: Instance of Config
    
    Returns:
        dict: Results summarizing tool performance across the dataset
    """

    # If current experiment was done on firefox, console output contains all passed resources
    # So what we need to do is remove those logged from all logged => rest is blocked
    try:
        if options.browser_type == "firefox":
            console_output = process_firefox_console_output(request_trees, console_output)
        else:
            console_output = parse_console_logs_chrome(console_output)
    except Exception:
        print("You probably mismatched browser and logs type! Or something more serious...")
        exit(GENERAL_ERROR)

    # Analyse each tree
    progress_printer = print_progress(len(request_trees), "Analysing blocked pages...")
    all_results = []

    for (_, tree) in request_trees.items():
        progress_printer()
        analysis_results = analyze_tree(tree, console_output)
        all_results.append(analysis_results)

    all_results = parse_partial_results(all_results)

    return all_results
