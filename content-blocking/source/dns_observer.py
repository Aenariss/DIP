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
        self.sniffer = AsyncSniffer(filter="udp port 53", prn=self.dns_callback, store=False)

    def start_sniffer(self) -> None:
        """Function to start the DNS sniffer"""
        
        # Start sniffing on UDP port 53 (DNS)
        # Important: The observed DNS responses may include additional DNS traffic
        # which came from other programs running on the host machine -- shouldn't matter
        self.sniffer.start()

    def stop_sniffer(self) -> None:
        """Function to stop the DNS sniffer"""
        # Check if the sniffer is still running
        if self.sniffer.running:
            self.sniffer.stop()

    def get_traffic(self) -> dict:
        return self.dns_responses
    
    def assign_cnames(self, cname_records: list, a_records: list) -> None:
        """Method to be maybe used in the future
           Goes through the CNAME chain and creates new record for each CNAME
           For CNAME record for X being A,B,C, creates A and sets it as CNAME of B
           and sets B as CNAME of C. To C, it assigns the A results for the original query. """
        # Go through CNAMEs and add its dedicated record for each CNAME
        n_of_cnames = len(cname_records)
        for i in range(n_of_cnames):
            cname = cname_records[i]
            tmp_assign_dict = {}

            # If it's not the last CNAME, just add it another CNAME
            if i+1 < n_of_cnames:
                following_cname = cname_records[i+1]
                tmp_assign_dict = {'A': [], 'CNAME': [following_cname]}

            # If it's the last CNAME, give it A resolution
            else:
                tmp_assign_dict = {'A': a_records, 'CNAME': []}

            # Only assign value if it was not already logged before
            if not self.dns_responses.get(cname):
                self.dns_responses[cname] = tmp_assign_dict
    
    # https://scapy.readthedocs.io/en/latest/api/scapy.layers.dns.html#scapy.layers.dns.DNS
    def dns_callback(self, packet: Packet) -> None:
        """Function to be used as callback with scapy sniffer"""
        # Check it's DNS response
        if packet.haslayer(DNS) and DNSRR in packet:
            dns_layer = packet.getlayer(DNS)

            # Requested page
            query_name = dns_layer.qd.qname.decode().rstrip('.')

            # Collected responses
            a_records = []
            cname_records = []
            for i in range(dns_layer.ancount):
                answer = dns_layer.an[i]

                # Check it's `A` record and if so add to the responses
                # type defitnition at: https://datatracker.ietf.org/doc/html/rfc1035#page-12
                if answer.type == 1:
                    a_records.append(answer.rdata)

                # If it's a `CNAME` record, store the alias
                elif answer.type == 5:
                    # Decode from binary and remove the dot on the right
                    cname_records.append(answer.rdata.decode().rstrip('.'))

            # If there was an A record, save it
            if a_records:
                # Already requested before
                if self.dns_responses.get(query_name):

                    # Overwrite the result (should be the same as before because of cache anyway)
                    self.dns_responses[query_name]['A'] = a_records

                else:
                    tmp_assign_dict = {'A': a_records, 'CNAME': []}
                    self.dns_responses[query_name] = tmp_assign_dict

            # If I logged a CNAME, save each CNAME as its own resolution
            if cname_records:
                # Already requested before
                if self.dns_responses.get(query_name):

                    # Add it to another array of responses
                    self.dns_responses[query_name]['CNAME'] = cname_records

                else:
                    tmp_assign_dict = {'A': [], 'CNAME': cname_records}
                    self.dns_responses[query_name] = tmp_assign_dict

                #self.assign_cnames(cname_records, a_records)
