# dns_repeater.py
# Edits the /etc/hosts file so that the observed IP addresses are used for DNS answers
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
import os
import tarfile
import time

# 3rd-party modules
import docker

# Custom modules
from source.constants import GENERAL_ERROR, DNS_CONTAINER_NAME, DNS_CONTAINER_IMAGE
from source.constants import DNS_CONFIGURATION_FOLDER, NAMED_CONF_FILE
from source.utils import print_progress

class DNSRepeater:
    """Class representing the object used to manipulate DNS server running in docker"""
    def __init__(self, dns_records: dict) -> None:
        """Method to initialize the DNS server. Loads the DNS data 
        from the given dict
        
        Args:
            dns_records: All DNS records squashed together
        """

        # Connect to docker (needs to be running!)
        try:
            self.docker_client = docker.from_env()
        except Exception:
            print("Could not load docker! Is Docker Desktop running?")
            exit(GENERAL_ERROR)

        # Initialize the container
        self.tar_file = "zones.tar"
        self.tar_path = DNS_CONFIGURATION_FOLDER + self.tar_file
        self.container = self._setup_container()
        self.original_config = None

        if not self.container:
            print("Could not initialize docker container! Stopping...")
            exit(GENERAL_ERROR)

        # Generate zone files content for each record
        self.prepare_config(dns_records)

        print("Custom DNS server initialized...")

    def untar_file(self) -> None:
        """Method to untar the tmp tarfile in the docker"""

        print("Extracting zone files inside the container...")

        untar_command = "docker exec {container} tar -xf /etc/bind/{tar_file} -C /etc/bind"\
            .format(tar_file=self.tar_file, container=DNS_CONTAINER_NAME)
        os.system(untar_command)

    def copy_to_container(self, file_to_copy: str, file_location: str,\
                            container: str=DNS_CONTAINER_NAME) -> None:
        """Method to copy given file to a selected location in /etc/bind/...
        in chosen container
        
        Args:
            file_to_copy: Path to the file to be copied to docker
            container: Name of the container to copy into
            file_location:
        """
        cp_command = f"docker cp {file_to_copy} {container}:/etc/bind/{file_location}"
        os.system(cp_command)

    def create_zone_config(self, domain: str) -> str:
        """Method to generate zone configuration to be put in named.conf
        
        Args:
            domain: Name of the zone

        Returns:
            str: Prepared zone configuration as a string
        """
        zone_config_template = \
            f"zone \"{domain}\" {{\n" +\
             "       type master;\n" +\
            f"       file \"/etc/bind/{domain}\";\n" +\
             "};\n"
        return zone_config_template

    def generate_zonefile(self, domain: str, all_subdomains: dict) -> str:
        """Method to generate zonfile for given domain
        
        Args:
            domain: Name of the zonefile
            all_subdomains: List of A and CNAME records in the zone file

        Returns:
            str: Zonefile generated as a string
        """

        zone_file = \
         ";\n" +\
         "$TTL    604800\n" +\
        f"@       IN      SOA     ownnstoavoidcollisions48a.{domain}.   root.{domain}. (\n" +\
         "                 2013012110         ; Serial\n" +\
         "                     604800         ; Refresh\n" +\
         "                      86400         ; Retry\n" +\
         "                    2419200         ; Expire\n" +\
         "                     604800 )       ; Negative Cache TTL\n" +\
         ";\n" +\
        f"@       IN      NS      ownnstoavoidcollisions48a.{domain}.\n" +\
         "ownnstoavoidcollisions48a       IN      A      127.0.0.1\n"

        # Iterate over all subdomains and edit zonefile accordingly
        for (subdomain, record) in all_subdomains.items():

            # If there is some CNAME-type record, only take the first and add record
            if record.get("CNAME", []) != []:
                first_cname = record["CNAME"][0]
                zone_file += f"{subdomain}       IN      CNAME    {first_cname}.\n"

                # If I added CNAME, continue (cant have same A and CNAME)
                continue

            # For A records, just write the first one
            first_a = record.get("A", [])
            if first_a:
                first_a = first_a[0]
                if domain == subdomain:
                    zone_file += f"@       IN      A       {first_a}\n"
                else:
                    zone_file += f"{subdomain}       IN      A       {first_a}\n"

        return zone_file

    def prepare_config(self, dns_records: dict) -> None:
        """Method to create zone files in the configuration folder
           The files will later be uploaded to the DNS server
           
        Args:
            dns_records: All DNS records squashed together
        """

        # Preserve the original config
        with open(NAMED_CONF_FILE, 'r', encoding='utf-8') as f:
            self.original_config = f.read()

        tar = tarfile.open(self.tar_path, mode='w')
        already_present = {}
        progress_printer = print_progress(len(dns_records.items()), "Generating zone files...")
        try:
            # Prepare new zone for each record
            for (key, value) in dns_records.items():
                progress_printer()
                zone_file = self.generate_zonefile(key, value)
                zone_file_path = DNS_CONFIGURATION_FOLDER + key

                # Write the file
                with open(zone_file_path, 'w', encoding='utf-8', newline="") as f:
                    f.write(zone_file)
                    f.write("\n")

                # Include it in named.conf
                with open(NAMED_CONF_FILE, 'a', encoding='utf-8', newline="") as f:
                    if not already_present.get(key):
                        already_present[key] = True
                        zone_config = self.create_zone_config(domain=key)
                        f.write(zone_config)
                        f.write("\n")

                # Add the zone to tmp tarfile
                tar.add(zone_file_path, arcname=os.path.basename(zone_file_path))
        except Exception:
            # Remove all zone files and tar from folder and docker
            print("Removing existing zone files...")
            for file in os.listdir(DNS_CONFIGURATION_FOLDER):
                filename = DNS_CONFIGURATION_FOLDER + file

                # Remove existing files except for the placeholder file
                if os.path.isfile(filename) and file != ".empty" and file != "named.conf":
                    os.remove(filename)

            with open(NAMED_CONF_FILE, 'w', encoding='utf-8', newline="") as f:
                f.write(self.original_config)

        tar.close()

        # Copy the tar and named.conf files into the docker
        self.copy_to_container(self.tar_path, self.tar_file)
        self.copy_to_container(NAMED_CONF_FILE, "named.conf")

    def find_container(self):
        """Method to find the DNS container
        
        Returns:
            any: The container running the BIND server
        """
        client = self.get_docker_client()

        all_containers = client.containers.list(all=True)
        container = None

        # Check if any of the containers matches the wanted name
        for c in all_containers:
            if c.name == DNS_CONTAINER_NAME:
                container = c
                break
        return container

    def get_container(self):
        """Method to return the container running the docker
        
        Returns:
            any: Container running the server
        """
        return self.container

    def _setup_container(self):
        """Method to get the container if it exists (even stopped), or create it if not
        
        Returns:
            any: Container running the server
        """

        client = self.get_docker_client()
        container = self.find_container()

        if not container:
        # If not running, create it
        # docker run --name=bind9 --publish 53:53/udp --publish 53:53/tcp\
        # internetsystemsconsortium/bind9:9.20
            client.containers.run(image=DNS_CONTAINER_IMAGE,
                                name=DNS_CONTAINER_NAME,
                                detach=True,
                                ports={
                                    "53/udp": 53,
                                    "53/tcp": 53,
                                }
            )

        # Find container again, should exist now
        return self.find_container()

    def get_docker_client(self) -> docker.DockerClient:
        """Method to return the docker client
        
        Returns:
            docker.DockerClient: client for communication with docker
        """
        return self.docker_client

    def start(self) -> None:
        """Method to start the container and set it as windows default DNS"""
        print("Starting the custom DNS server...")

        # Set 127.0.0.1 as DNS server
        c = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
        c += 'Set-DnsClientServerAddress -InterfaceAlias '
        c += '\'Ethernet\' -ServerAddresses 127.0.0.1"'
        os.system(c)

        container = self.get_container()
        container.start()

        self.untar_file()
        self.restart()

    def stop(self) -> None:
        """Method to stop repeating DNS responses -> Stop the docker and restore DNS settings"""
        print("Stopping the custom DNS server...")

        # Set DHCP as default for DNS server IP
        c = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
        c += 'Set-DnsClientServerAddress -InterfaceAlias \"Ethernet\" -ResetServerAddresses"'
        os.system(c)

        # Remove all zone files and tar from folder and docker
        print("Removing existing zone files...")
        for file in os.listdir(DNS_CONFIGURATION_FOLDER):
            filename = DNS_CONFIGURATION_FOLDER + file

            # Remove existing file except for the placeholder file
            if os.path.isfile(filename) and file != ".empty" and file != "named.conf":
                os.remove(filename)

        # Remove all settings form docker
        rm_command = "docker exec {container} rm -rf /etc/bind/*"\
            .format(container=DNS_CONTAINER_NAME)
        os.system(rm_command)

        # Restore original named.conf
        with open(NAMED_CONF_FILE, 'w', encoding='utf-8', newline="") as f:
            f.write(self.original_config)

        # Upload named.conf to docker
        self.copy_to_container(NAMED_CONF_FILE, "named.conf")

        container = self.get_container()
        container.stop()

    def restart(self) -> None:
        """Method to restart the container"""
        container = self.get_container()
        container.stop()
        time.sleep(0.5)
        container.start()
