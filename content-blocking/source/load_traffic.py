# load_traffic.py
# Observe traffic on given pages and save it into a file.
# Also observe the corresponding DNS responses.
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
import json
from functools import partial

# 3rd-party modules
from scapy.packet import Packet
from scapy.all import AsyncSniffer
from scapy.layers.dns import DNSRR, DNS

# Custom modules
from source.file_loading import load_pages
from source.page_http_traffic import get_page_traffic
from source.constants import TRAFFIC_FOLDER, FILE_ERROR

def load_traffic(options: dict) -> None:
    """Function to observe traffic on given list of pages"""
    pages = load_pages()

    # Counter to name files like 1.json, 2.json... to prevent issues
    filename_counter = 1

    # Go through each page and observe traffic
    for page in pages:

        dns_traffic = {}

        # Make the callback for sniffer use additional argument (dict containing the results)
        callback = partial(dns_callback, dns_responses=dns_traffic)

        # Start sniffing on UDP port 53 (DNS)
        # Important: The observed DNS responses may include additional DNS traffic
        # which came from other programs running on the host machine -- shouldn't matter
        sniffer = AsyncSniffer(filter="udp port 53", prn=callback, store=False)
        sniffer.start()

        # Get the HTTP(S) traffic associated with a page
        traffic = get_page_traffic(page, options)

        # Stop sniffing and get the observed DNS responses
        sniffer.stop()

        save_traffic(dns_traffic, page, str(filename_counter), "dns")
        save_traffic(traffic, page, str(filename_counter), "http")
        filename_counter += 1

def save_traffic(traffic: dict, pagename: str, filename: str, traffic_type: str) -> None:
    """Function to append observed traffic to the traffic file"""
    try:
        f = None
        if traffic_type == "dns":
            f = open(TRAFFIC_FOLDER + filename + '_dns' + '.json', 'w', encoding='utf-8')
        else:
            f = open(TRAFFIC_FOLDER + filename + '.json', 'w', encoding='utf-8')
        # Format the dictionary as json
        jsoned_traffic = json.dumps(traffic, indent=4)
        f.write(jsoned_traffic)
        f.close()

    except OSError as error:
        print("Could not save traffic to a file! Problem with page:", pagename)
        print(error)
        exit(FILE_ERROR)

def dns_callback(packet: Packet, dns_responses: dict) -> None:
    """Function to be used as callback with scapy sniffer"""
    # Check it's DNS response
    if packet.haslayer(DNS) and DNSRR in packet:
        dns_layer = packet.getlayer(DNS)

        # Requested page
        query_name = dns_layer.qd.qname.decode().rstrip('.')

        # Collected responses
        a_records = []
        for i in range(dns_layer.ancount):
            answer = dns_layer.an[i]

            # Check it's `A` record and if so add to the responses
            if answer.type == 1:
                a_records.append(answer.rdata)

        # If there was an A record, save it
        if a_records:
            dns_responses[query_name] = a_records
