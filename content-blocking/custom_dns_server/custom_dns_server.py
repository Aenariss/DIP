### WILL PROBABLY NOT BE USED

# custom_dns_server.py
# Replay observed DNS traffic from a given file.
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

# Default modules
from multiprocessing import Process
from socketserver import UDPServer, BaseRequestHandler

# 3rd-party modules
from dnslib import DNSRecord, RR, QTYPE, A

class DNSHandler(BaseRequestHandler):
    """Class to handle DNS replies"""
    def handle(self):
        """Override base class handle method"""
        print("Handling a packet")
        data, socket = self.request
        request = DNSRecord.parse(data)

        # Get name for which the client is asking
        qname = request.q.qname
        print(f"Received query for: {qname}")

        # Replay logged response
        reply = request.reply()
        reply.add_answer(RR(qname, QTYPE.A, rdata=A("127.0.0.1"))) 

        # Send the response
        socket.sendto(reply.pack(), self.client_address)

def run_dns_server(request_tree: dict):
    """Function to launch custom DNS server"""

    # Run the server on custom port 53
    server = UDPServer(("0.0.0.0", 53), DNSHandler)

    print("DNS Server is running on port 53...")
    server.serve_forever()

def start_dns_server(request_tree: dict):
    # TBD: will need to compute its own resource tree later
    """Function to start the DNS server to replay logged DNS replies"""
    print("Starting the DNS server...")

    # Start another process running the server
    server = Process(target=run_dns_server, args=(request_tree, ))
    server.start()
    return server

def stop_dns_server(server):
    """Function to stop the DNS server"""
    print("Stopping the DNS server...")
    server.terminate()
    server.join()

if __name__ == "__main__":
    run_dns_server({})