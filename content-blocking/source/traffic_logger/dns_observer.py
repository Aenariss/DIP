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
        """Method to initialize the sniffer"""

        self.dns_responses = {}
        self.sniffer = AsyncSniffer(filter="udp port 53", prn=self.store_packet, store=False)
        self.packets = []

    def start_sniffer(self) -> None:
        """Method to start the DNS sniffer"""

        # Start sniffing on UDP port 53 (DNS)
        # Important: The observed DNS responses may include additional DNS traffic
        # which came from other programs running on the host machine -- shouldn't matter
        self.sniffer.start()

    def stop_sniffer(self) -> None:
        """Method to stop the DNS sniffer"""
        # Check if the sniffer is still running
        if self.sniffer.running:
            self.sniffer.stop()

    def store_packet(self, packet: Packet) -> None:
        """Method to store DNS packet into internal list"""
        self.packets.append(packet)

    def get_traffic(self) -> dict:
        """Method to obtain the saved DNS responses
        
            Returns:
                dict: Dictionary containing records of observed DNS responses.
                    First-level keys can be used as names of zone files, secnod-level
                    keys can be used as names of records in the zone file
        """
        for packet in self.packets:
            self.parse_dns_packet(packet)

        return self.dns_responses

    def _obtain_subdomains(self, query_name: str) -> tuple[str, str]:
        """Method to split address into its subdomains
            Return the nam of the record and also the zone name
           
            Args:
                query_name: The name of the original query

            Returns:
                tuple:
                    - main_zone_name(str): 2nd and 1st level domain of the original query, 
                    for *test.example.com*, returns *example.com*
                    - subdomains(str): Rest of the subdomains, for *test.a.com*, returns *test*
        """

        # Try to split the domain into subdomains (example.com = example, com)
        domains = query_name.split('.')
        main_zone_name = domains[-2] + '.' + domains[-1]

        # Get the rest of the domains in the address
        remain = domains[:-2]

        # If there were subdomains left, they are the key. Else, zone_name is the key.
        subdomains = main_zone_name
        if remain:
            subdomains = '.'.join(remain)

        return main_zone_name, subdomains

    def _assign_cnames(self, two_highest_level_domains: str, remaining_subdomain: str,\
                        cname_records: list[str]) -> None:
        """Goes through the CNAME chain and creates new record for each CNAME
           For CNAME record for X being A,B,C, creates A and sets it as CNAME of B
           and sets B as CNAME of C. To C, it assigns the A results for the original query. 

           Args:
            two_highest_level_domains: The two highest-level domains of the original query
                (test.example.com -> example.com)
            remaining_subdomain: Rest of the original queried domain (test.example.com -> test)
            cname_records: List of all CNAME records
        """

        # Go through CNAMEs and add a dedicated record for each CNAME
        n_of_cnames = len(cname_records)
        for i in range(n_of_cnames):
            cname = cname_records[i]
            tmp_assign_dict = {}
            tmp_assign_dict_new = {}

            primary_zone_key, subdomains = self._obtain_subdomains(cname)

            # If it's not the last CNAME, just add it another CNAME
            if i+1 < n_of_cnames:
                following_cname = cname_records[i+1]
                tmp_assign_dict = {'A': [], 'CNAME': [following_cname]}

            # If it's the last CNAME, give it an A resolution
            else:
                zone_records = self.dns_responses.get(two_highest_level_domains)
                a_records = []

                # If record for zone exists, obtain the a_records from already existing domain
                # if it exists
                if zone_records:
                    domain_record = self.dns_responses[two_highest_level_domains].get(\
                        remaining_subdomain)
                    a_records = domain_record.get('A', [])

                tmp_assign_dict = {'A': a_records, 'CNAME': []}

            tmp_assign_dict_new = {subdomains: tmp_assign_dict}

            # Check if it already exists and if not, create it. Else use existing A response.
            if not self.dns_responses.get(primary_zone_key):
                self.dns_responses[primary_zone_key] = tmp_assign_dict_new
            else:
                self.dns_responses[primary_zone_key][subdomains] = tmp_assign_dict

    def _process_dns_answers(self, dns_layer: Packet) -> tuple[list[str], list[str]]:
        """Internal method to process answers in DNS layer
        
        Args:
            dns_layer: The DNS layer of the received DNS packet
        
        Returns:
            tuple:
            - a_records (list[str]): The first list contains 'A' record reponses - IP addresses
            - cname_records (list[str]): The second list contains 'CNAME' responses - aliases
        """

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

        return a_records, cname_records

    def _save_dns_answer(self, two_highest_level_domains: str, subdomain: str, a_records: list,\
                        cname_records: list) -> None:
        """Internal method to log the DNS response to self.dns_responses
        
        Args:
            two_highest_level_domains: The two highest-level domains of the original query
                (test.example.com -> example.com)
            subdomain: All subdomains of 3rd and lower order, 
                for test.example.com, this would be *test*.
            a_records: List of received A responses
            cname_records: List of received CNAME responses
        """

         # If there was an A record, save it
        if a_records:
            # Already requested before
            if self.dns_responses.get(two_highest_level_domains):
                if self.dns_responses[two_highest_level_domains].get(subdomain):

                    # Overwrite the result (should be the same because of cache anyway)
                    self.dns_responses[two_highest_level_domains][subdomain]['A'] = a_records

                # New zone_key
                else:
                    self.dns_responses[two_highest_level_domains][subdomain] = \
                        {'A': a_records, 'CNAME': []}
            else:
                tmp_assign_dict = {subdomain:{'A': a_records, 'CNAME': []}}
                self.dns_responses[two_highest_level_domains] = tmp_assign_dict

        # If I logged a CNAME, save each CNAME as its own resolution
        if cname_records:
            # Already requested before
            if self.dns_responses.get(two_highest_level_domains):
                if self.dns_responses[two_highest_level_domains].get(subdomain):

                    # Overwrite source
                    self.dns_responses[two_highest_level_domains][subdomain]['CNAME'] = \
                        cname_records

                # New zone_key
                else:
                    self.dns_responses[two_highest_level_domains][subdomain] = \
                        {'A': [], 'CNAME': cname_records}
            else:
                tmp_assign_dict = {subdomain: {'A': [], 'CNAME': cname_records}}
                self.dns_responses[two_highest_level_domains] = tmp_assign_dict

            # For each observed cname, assign it its own record
            self._assign_cnames(two_highest_level_domains, subdomain, cname_records)

    # https://scapy.readthedocs.io/en/latest/api/scapy.layers.dns.html#scapy.layers.dns.DNS
    def parse_dns_packet(self, packet: Packet) -> None:
        """Function to be used for each sniffed packet
        
        Args:
            packet: The DNS packet to process
        """
        # Check it's DNS response
        if packet.haslayer(DNS) and DNSRR in packet:
            dns_layer = packet.getlayer(DNS)

            # Requested page
            query_name = dns_layer.qd.qname.decode().rstrip('.')
            primary_zone_name, subdomain = self._obtain_subdomains(query_name)

            # Collected responses
            a_records, cname_records = self._process_dns_answers(dns_layer)

            # Save the responses into dict
            self._save_dns_answer(primary_zone_name, subdomain, a_records, cname_records)
