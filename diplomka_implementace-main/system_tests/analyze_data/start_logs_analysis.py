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

import levenshtein_distance as levenshtein
import cosine_similarity as cosine
import simple_comparison as simple
import io_funcs as io

import sys
sys.path.append("/usr/app/src/get_data")
from configuration import Config


## Build header of output HTML file.
def html_header():
    return "<html>" \
           "<head><title>Logs comparison</title>" \
           "<style>" \
           "body {background-color: white} " \
           "table {width: 100%; border-collapse: collapse; table-layout: fixed;} " \
           ".added-log {background-color: LightPink} " \
           "h2 {margin-left: 10px;} " \
           "th, td {width: 50%; border: 1px solid black; word-wrap: break-word; padding: 5px;} " \
           ".colored-results-table-visible td {width: 33%; border: none; padding: 5px; color: white; text-align: center;} " \
           ".colored-results-table-visible .method {background-color: red;} " \
           ".colored-results-table {display: none;} " \
           ".colored-results-table-visible {display: table; margin-bottom: 5px} " \
           "</style>" \
           "</head>" \
           "<body><h1>Logs comparison</h1>"


## Build footer of output HTML file.
def html_footer():
    return "<br><br></body></html>"


## Build table with logs for one site. Insert to output HTML file.
def build_site_logs_table(site, site_number):
    ext_names = [Config.extensions_dict_names_chrome.get(ext, ext) for ext in Config._extensions_to_test]
    ext_names  = ' '.join(ext_names)
    output = "<br><h2>" + str(site_number) + ") " + site['site'] + "</h2><table><tr><th>Without addon</th><th>With " + ext_names  + " </th></tr>"
    i = 0
    max_lenght = 0
    if site['logs_without_addon'] == "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE":
            output += "<tr><td>"
            output += "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE"
            output += "</td><td"
            output_tmp = "><tr>"
            output += '><table class="colored-results-table"'
            output += output_tmp + '</tr></table>'
            output += "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE"
            output += "</td></tr>"
            output += "</table>"
            return output
    if site['logs_with_addon'] != "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE":
        max_lenght = max(len(site['logs_without_addon']), len(site['logs_with_addon']))
    else:
        if site['logs_without_addon'] != "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE":
            max_lenght = len(site['logs_without_addon'])

    while i < max_lenght:
        output += "<tr><td>"
        if i < len(site['logs_without_addon']):
            output += "Level: " + site['logs_without_addon'][i]['level'] + "<br>"
            output += "Source: " + site['logs_without_addon'][i]['source'] + "<br>"
            output += "Message: " + site['logs_without_addon'][i]['message']
        output += "</td><td"
        output_tmp = "><tr>"
        colored_results_table_visible = False
        if site['logs_with_addon'] != "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE":
            if i < len(site['logs_with_addon']):
                output_tmp += "<td"
                if simple.was_log_added(site['logs_with_addon'][i], site['logs_without_addon']):
                    output_tmp += ' class="method">Simple comparison</td><td'
                    colored_results_table_visible = True
                else:
                    output_tmp += "></td><td"
                if levenshtein.was_log_added(site['logs_with_addon'][i], site['logs_without_addon']):
                    output_tmp += ' class="method">Levenshtein distance</td><td'
                    colored_results_table_visible = True
                else:
                    output_tmp += "></td><td"
                if cosine.was_log_added(site['logs_with_addon'][i], site['logs_without_addon']):
                    output_tmp += ' class="method">Cosine similarity</td>'
                    colored_results_table_visible = True
                else:
                    output_tmp += "></td>"

        if colored_results_table_visible:
            output += ' class="added-log"><table class="colored-results-table-visible"'
        else:
            output += '><table class="colored-results-table"'
        output += output_tmp + '</tr></table>'
        if site['logs_with_addon'] != "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE":
            if i < len(site['logs_with_addon']):
                    output += "Level: " + site['logs_with_addon'][i]['level'] + "<br>"
                    output += "Source: " + site['logs_with_addon'][i]['source'] + "<br>"
                    output += "Message: " + site['logs_with_addon'][i]['message']
        elif i == 0:
            output += "ERROR_WHILE_LOADING_THIS_OR_PREVIOUS_PAGE"
        output += "</td></tr>"
        i += 1
    output += "</table>"
    return output


## Main function of logs analysis.
def main():
    io.delete_file_if_exists("../data/logs/logs_comparison.html")

    sites_logs = io.get_json_file_content("../data/logs/logs.json")

    output = html_header()
    j = 1
    sites_number = len(sites_logs)
    if sites_number == 0:
        print("No logs for analysis found. Please, include getting logs to configuration and run getting data first.")
    for site in sites_logs:
        print("Site " + str(j) + " of " + str(sites_number) + ": " + site['site'])
        output += build_site_logs_table(site, j)
        j += 1
    output += html_footer()

    io.write_file("../data/logs/logs_comparison.html", output)


if __name__ == "__main__":
    main()
