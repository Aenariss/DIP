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

    def generate_zone_key(self, query_name: str) -> tuple[str, str]:
        """Method to split address into its subdomains
           Return the nam of the record and also the zone name"""
        # Try to split the domain into subdomains (example.com = example, com)
        domains = query_name.split('.')
        zone_name = domains[-2] + '.' + domains[-1]
        query_name = zone_name

        # Get the rest of the domains in the address
        remain = domains[:-2]

        # If there were subdomains left, they are the key. Else, zone_name is the key.
        zone_key = zone_name
        if remain:
            zone_key = '.'.join(remain)

        return query_name, zone_key

    def assign_cnames(self, original_query: str, original_zone: str, cname_records: list) -> None:
        """
           Goes through the CNAME chain and creates new record for each CNAME
           For CNAME record for X being A,B,C, creates A and sets it as CNAME of B
           and sets B as CNAME of C. To C, it assigns the A results for the original query. """
        # Go through CNAMEs and add its dedicated record for each CNAME
        n_of_cnames = len(cname_records)
        for i in range(n_of_cnames):
            cname = cname_records[i]
            tmp_assign_dict = {}
            tmp_assign_dict_new = {}

            query_name, zone_key = self.generate_zone_key(cname)

            # If it's not the last CNAME, just add it another CNAME
            if i+1 < n_of_cnames:
                following_cname = cname_records[i+1]
                tmp_assign_dict = {'A': [], 'CNAME': [following_cname]}

            # If it's the last CNAME, give it A resolution
            else:
                zone_records = self.dns_responses.get(original_query)
                a_records = []

                # If record for zone exists, obtain the a_records from corresponding domain
                if zone_records:
                    domain_record = self.dns_responses[original_query].get(original_zone)
                    a_records = domain_record.get('A', [])

                tmp_assign_dict = {'A': a_records, 'CNAME': []}

            tmp_assign_dict_new = {zone_key: tmp_assign_dict}

            if not self.dns_responses.get(query_name):
                self.dns_responses[query_name] = tmp_assign_dict_new
            else:
                self.dns_responses[query_name][zone_key] = tmp_assign_dict

    # https://scapy.readthedocs.io/en/latest/api/scapy.layers.dns.html#scapy.layers.dns.DNS
    def dns_callback(self, packet: Packet) -> None:
        """Function to be used as callback with scapy sniffer"""
        # Check it's DNS response
        if packet.haslayer(DNS) and DNSRR in packet:
            dns_layer = packet.getlayer(DNS)

            # Requested page
            query_name = dns_layer.qd.qname.decode().rstrip('.')

            query_name, zone_key = self.generate_zone_key(query_name)

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
                    if self.dns_responses[query_name].get(zone_key):

                        # Overwrite the result (should be the same because of cache anyway)
                        self.dns_responses[query_name][zone_key]['A'] = a_records

                    # New zone_key
                    else:
                        self.dns_responses[query_name][zone_key] = {'A': a_records, 'CNAME': []}
                else:
                    tmp_assign_dict = {zone_key:{'A': a_records, 'CNAME': []}}
                    self.dns_responses[query_name] = tmp_assign_dict

            # If I logged a CNAME, save each CNAME as its own resolution
            if cname_records:
                # Already requested before
                if self.dns_responses.get(query_name):
                    if self.dns_responses[query_name].get(zone_key):

                        # Overwrite source
                        self.dns_responses[query_name][zone_key]['CNAME'] = cname_records

                    # New zone_key
                    else:
                        self.dns_responses[query_name][zone_key] = {'A': [], 'CNAME': cname_records}
                else:
                    tmp_assign_dict = {zone_key: {'A': [], 'CNAME': cname_records}}
                    self.dns_responses[query_name] = tmp_assign_dict

                self.assign_cnames(query_name, zone_key, cname_records)
