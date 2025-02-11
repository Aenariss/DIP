# dns_observer.py
# Observe DNS traffic while a page is being visited.
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

# 3rd-party modules
from scapy.packet import Packet
from scapy.all import AsyncSniffer
from scapy.layers.dns import DNSRR, DNS

class DNSSniffer():
    def __init__(self):
        """Method to initialize the sniffer
        """

        self.dns_responses = {}
        self.sniffer = None

    def start_sniffer(self) -> None:
        """Function to start the DNS sniffer"""
        
        # Start sniffing on UDP port 53 (DNS)
        # Important: The observed DNS responses may include additional DNS traffic
        # which came from other programs running on the host machine -- shouldn't matter
        self.sniffer = AsyncSniffer(filter="udp port 53", prn=self.dns_callback, store=False)
        self.sniffer.start()

    def stop_sniffer(self) -> None:
        """Function to stop the DNS sniffer"""
        self.sniffer.stop()

    def get_traffic(self) -> dict:
        return self.dns_responses
    
    def dns_callback(self, packet: Packet) -> None:
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
                # Already requested before
                if self.dns_responses.get(query_name):

                    # Add it to another array of responses
                    self.dns_responses[query_name].extend([a_records])

                self.dns_responses[query_name] = [a_records]
