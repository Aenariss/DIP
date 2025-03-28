# test_dns_sniffer.py
# Test the functions used in DNS Sniffer from traffic_logger
# https://0xbharath.github.io/art-of-packet-crafting-with-scapy/scapy/creating_packets/index.html
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
import unittest

# 3rd party modules
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.packet import Packet

# Custom modules
from source.traffic_logger import dns_observer

class TestDNSCallback(unittest.TestCase):
    def setUp(self):
        """Set up an instance of YourClass before each test"""
        self.dns_sniffer_class = dns_observer.DNSSniffer()

        # Set-up parameters for fake DNS packets
        self.dns_src = "1.1.1.1"
        self.dns_dst = "2.2.2.2"

    def _craft_dns_packet(self, query: str, a_replies: list, cname_replies: list)\
        -> Packet:
        """Internal method to create a DNS reply packet to be used for testing
        
            Args:
                query: Name of the original query
                a_replies: list of IP addresses to be used in replies
                cname_replies: list of CNAME aliases to be used in replies

            Returns:
                Packet: The crafted DNS packet
        """

        l2 = Ether()
        l3 = IP(src=self.dns_src, dst=self.dns_dst)
        l4 = UDP(sport=4242, dport=53)

        an = []
        previous_cname = query
        for cname in cname_replies:
            an.append(DNSRR(rrname=previous_cname, type=5, rdata=cname))

            # Next CNAME points to this one
            previous_cname = cname

        # Craft `A` replies
        for ip in a_replies:
            an.append(DNSRR(type=1, rdata=ip))

        l5 = DNS(qd=DNSQR(qname=query), ancount=len(an),\
                an=an)

        test_packet = l2 / l3 / l4 / l5

        return test_packet

    def test_subdomains_obtaining(self):
        """Test _obtain_subdomains() works as intended"""

        query = "long.test.example.com"
        primary_zone, subdomains = self.dns_sniffer_class._obtain_subdomains(query)

        self.assertEqual(primary_zone, "example.com")
        self.assertEqual(subdomains, "long.test")

    def test_no_subdomain(self):
        """Test to check if page with no 3-rd and further subdomains is logged ok"""
        query = "example.com"
        primary_zone, subdomains = self.dns_sniffer_class._obtain_subdomains(query)

        self.assertEqual(primary_zone, "example.com")
        self.assertEqual(subdomains, "example.com")

    def test_record_assigning(self):
        """Test _process_dns_answers() correctly returns A and CNAME records"""

        test_packet = self._craft_dns_packet("test.example.com",\
                                a_replies=["192.168.0.1"], cname_replies=[])

        a_records, cname_records = \
            self.dns_sniffer_class._process_dns_answers(test_packet.getlayer('DNS'))

        self.assertEqual(a_records, ["192.168.0.1"])
        self.assertEqual(cname_records, [])

        test_packet = self._craft_dns_packet("test.example.com",\
                                a_replies=["192.168.0.1", "192.168.0.2"], cname_replies=[])

        a_records, cname_records = \
            self.dns_sniffer_class._process_dns_answers(test_packet.getlayer('DNS'))

        self.assertEqual(a_records, ["192.168.0.1", "192.168.0.2"])
        self.assertEqual(cname_records, [])

        test_packet = self._craft_dns_packet("test.example.com",\
                a_replies=["192.168.0.1", "192.168.0.2"], cname_replies=["next.test.example.com"])

        a_records, cname_records = \
            self.dns_sniffer_class._process_dns_answers(test_packet.getlayer('DNS'))

        self.assertEqual(a_records, ["192.168.0.1", "192.168.0.2"])
        self.assertEqual(cname_records, ["next.test.example.com"])

    def test_dns_callback_a_record(self):
        """Test that parse_dns_packet() works as intended for A replies"""

        test_packet = self._craft_dns_packet("next.test.example.com",\
                                        a_replies=["192.168.0.1"], cname_replies=[])
        self.dns_sniffer_class.parse_dns_packet(test_packet)

        test_packet = self._craft_dns_packet("domain.example.com",\
                                        a_replies=["192.168.0.2"], cname_replies=[])
        self.dns_sniffer_class.parse_dns_packet(test_packet)

        test_packet = self._craft_dns_packet("new-example.com",\
                                        a_replies=["192.168.0.3"], cname_replies=[])
        self.dns_sniffer_class.parse_dns_packet(test_packet)

        test_packet = self._craft_dns_packet("test.test.com",\
                                        a_replies=["192.168.0.4"], cname_replies=[])
        self.dns_sniffer_class.parse_dns_packet(test_packet)

        # top and second-level domains need to be keys in dict
        self.assertIn("example.com", self.dns_sniffer_class.dns_responses)
        self.assertIn("new-example.com", self.dns_sniffer_class.dns_responses)
        self.assertIn("test.com", self.dns_sniffer_class.dns_responses)

        example_com_records = self.dns_sniffer_class.dns_responses["example.com"]
        new_example_records = self.dns_sniffer_class.dns_responses["new-example.com"]
        test_test_com_records = self.dns_sniffer_class.dns_responses["test.com"]

        # example.com must have 2 subkeys - next.test and domain
        self.assertIn("next.test", example_com_records)
        self.assertIn("domain", example_com_records)

        # If no subdomains, it must have itself
        self.assertIn("new-example.com", new_example_records)

        # test.com should have test as record
        self.assertIn("test", test_test_com_records)

        # They must also have corresponding IP addresses
        domain_example_com_a = example_com_records["domain"].get("A", [])
        next_test_example_com_a = example_com_records["next.test"].get("A", [])
        test_test_com_a = test_test_com_records["test"].get("A", [])
        new_example_a = new_example_records["new-example.com"].get("A", [])

        self.assertEqual(domain_example_com_a, ["192.168.0.2"])
        self.assertEqual(next_test_example_com_a, ["192.168.0.1"])
        self.assertEqual(new_example_a, ["192.168.0.3"])
        self.assertEqual(test_test_com_a, ["192.168.0.4"])

    def test_dns_callback_cname_record(self):
        """Test that parse_dns_packet() works as intended for CNAME replies"""

        test_packet = self._craft_dns_packet("next.test.example.com",\
            a_replies=["192.168.0.1"], cname_replies=["cname.example.com", "different.page.cz"])
        self.dns_sniffer_class.parse_dns_packet(test_packet)

        test_packet = self._craft_dns_packet("new-example.com",\
                            a_replies=["192.168.0.3"], cname_replies=["only_one.com"])
        self.dns_sniffer_class.parse_dns_packet(test_packet)


        # top and second-level domains need to be keys in dict, also must hold true for all CNAMEs
        self.assertIn("example.com", self.dns_sniffer_class.dns_responses)
        self.assertIn("new-example.com", self.dns_sniffer_class.dns_responses)
        self.assertIn("page.cz", self.dns_sniffer_class.dns_responses)
        self.assertIn("only_one.com", self.dns_sniffer_class.dns_responses)

        example_com_records = self.dns_sniffer_class.dns_responses["example.com"]
        new_example_records = self.dns_sniffer_class.dns_responses["new-example.com"]
        page_cz_records = self.dns_sniffer_class.dns_responses["page.cz"]
        only_one_records = self.dns_sniffer_class.dns_responses["only_one.com"]

        # subkeys need to be included
        self.assertIn("next.test", example_com_records)
        self.assertIn("cname", example_com_records)
        self.assertIn("different", page_cz_records)

        # If no subdomains, it must have itself
        self.assertIn("new-example.com", new_example_records)
        self.assertIn("only_one.com", only_one_records)

        next_test_example_com_cname = example_com_records["next.test"].get("CNAME", [])
        cname_example_com_cname = example_com_records["cname"].get("CNAME", [])

        different_page_a = page_cz_records["different"].get("A", [])
        different_page_cname = page_cz_records["different"].get("CNAME", [])

        new_example_cname = new_example_records["new-example.com"].get("CNAME", [])
        only_one_a = only_one_records["only_one.com"].get("A", [])
        only_one_cname = only_one_records["only_one.com"].get("CNAME", [])

        # First record in chain must have its own CNAMEs
        self.assertEqual(next_test_example_com_cname, ["cname.example.com", "different.page.cz"])

        # cname.example.com needs to have different.page.cz as CNAME
        self.assertEqual(cname_example_com_cname, ["different.page.cz"])

        # different.page.cz must have the original 192.168.0.1 as its A record and no other CNAMEs
        self.assertEqual(different_page_a, ["192.168.0.1"])
        self.assertEqual(different_page_cname, [])

        # new-example.com must have only_one.com as CNAME and only_one must have original IP as A
        self.assertEqual(new_example_cname, ["only_one.com"])
        self.assertEqual(only_one_a, ["192.168.0.3"])
        self.assertEqual(only_one_cname, [])
