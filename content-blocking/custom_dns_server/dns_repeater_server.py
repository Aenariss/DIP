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

# 3rd-party modules
import docker

# Custom modules
from source.constants import GENERAL_ERROR, DNS_CONTAINER_NAME, DNS_CONTAINER_IMAGE
from source.constants import DNS_CONFIGURATION_FOLDER

class DNSRepeater:
    """Class representing the object used to manipulate DNS server running in docker"""
    def __init__(self, dns_records: dict) -> None:
        """Method to initialize the DNS server. Loads the DNS data 
        from the given dict"""

        # Connect to docker (needs to be running!)
        try:
            self.docker_client = docker.from_env()
        except Exception:
            print("Could not load docker! Is Docker Desktop running?")
            exit(GENERAL_ERROR)

        # Initialize the container
        self.container = self.__setup_container()
        self.original_config = None

        if not self.container:
            print("Could not initialize docker container! Stopping...")
            exit(GENERAL_ERROR)

        # Generate zone files content for each record
        self.prepare_config(dns_records)

        print("Custom DNS server initialized...")

    def prepare_config(self, dns_records: dict) -> None:
        """Method to create zone files in the configuration folder
           The files will later be uploaded to the DNS server"""
        named_conf_file = DNS_CONFIGURATION_FOLDER + "named.conf"
        with open(named_conf_file, 'r', encoding='utf-8') as f:
            self.original_config = f.read()

        # Template for adding new zones into named.cnf
        zone_config_template = """
zone "{domain}" {{
        type master;
        file "/etc/bind/{domain}";
}};
"""

        # Prepare new zone for each record
        for (key, value) in dns_records.items():
            zone_file = self.generate_zonefile(key, value)
            zone_file_path = DNS_CONFIGURATION_FOLDER + key

            # Write the file
            with open(zone_file_path, 'w', encoding='utf-8', newline="") as f:
                f.write(zone_file)
                f.write("\n")

            # Include it in named.conf
            with open(named_conf_file, 'a', encoding='utf-8', newline="") as f:
                zone_config = zone_config_template.format(domain=key)
                f.write(zone_config)
                f.write("\n")

            # Copy the file into the docker
            cp_command = "docker cp {zone_file} {container}:/etc/bind/{file}"\
                .format(zone_file=zone_file_path, file=key, container=DNS_CONTAINER_NAME)
            os.system(cp_command)

        # Copy the named.conf into the docker
        cp_command = "docker cp {named_conf_file} {container}:/etc/bind/{file}"\
        .format(named_conf_file=named_conf_file, container=DNS_CONTAINER_NAME, file="named.conf")
        os.system(cp_command)


    def generate_zonefile(self, domain: str, all_subdomains: dict) -> str:
        """Method to generate zonfile for given domain"""

        # zonefile header
        zone_file = f"""
;
$TTL    604800
@       IN      SOA     ns.{domain}.   root.{domain}. (
                 2013012110         ; Serial
                     604800         ; Refresh
                      86400         ; Retry
                    2419200         ; Expire
                     604800 )       ; Negative Cache TTL
;
@       IN      NS      ns.{domain}.
ns      IN      A       127.0.0.1
"""
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

    def find_container(self):
        """Method to find the DNS container"""
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
        return self.container

    def __setup_container(self) -> None:
        """Method to get the container if it exists (even stopped), or create it if not"""

        client = self.get_docker_client()

        container = self.find_container()

        if not container:

        # If not, create it
        # docker run -it --name=bind9 --restart=always --publish 53:53/udp --publish 53:53/tcp\
        #  --publish 127.0.0.1:953:953/tcp --volume /etc/bind --volume /var/cache/bind\
        #  --volume /var/lib/bind --volume /var/log internetsystemsconsortium/bind9:9.20

            client.containers.run(image=DNS_CONTAINER_IMAGE,
                                name=DNS_CONTAINER_NAME,
                                detach=True,
                                restart_policy={"Name": "always"},
                                ports={
                                    "53/udp": 53,
                                    "53/tcp": 53,
                                    "953/tcp": "127.0.0.1:953"
                                },
                                volumes={
                                    "/etc/bind": {"bind": "/etc/bind", "mode": "rw"},
                                    "/var/cache/bind": {"bind": "/var/cache/bind", "mode": "rw"},
                                    "/var/lib/bind": {"bind": "/var/lib/bind", "mode": "rw"},
                                    "/var/log": {"bind": "/var/log", "mode": "rw"}
                                }
            )

        # Find container again, should exist now
        return self.find_container()

    def get_docker_client(self) -> docker.DockerClient:
        """Methodd to return the docker client"""
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

    def stop(self) -> None:
        """Method to stop repeating DNS responses -> Stop the docker and restore DNS settings"""
        print("Stopping the custom DNS server...")

        # Set DHCP as default for DNS server IP
        c = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
        c += 'Set-DnsClientServerAddress -InterfaceAlias \"Ethernet\" -ResetServerAddresses"'
        os.system(c)

        # Remove all zone files from folder and docker
        print("Removing existing zone files...")
        for file in os.listdir(DNS_CONFIGURATION_FOLDER):
            filename = DNS_CONFIGURATION_FOLDER + file

            # Remove file form docker
            cp_command = "docker exec {container} rm -rf /etc/bind/{file}"\
                .format(file=file, container=DNS_CONTAINER_NAME)
            os.system(cp_command)

            # Remove existing file except for the placeholder file
            if os.path.isfile(filename) and file != ".empty" and file != "named.conf":
                os.remove(filename)

        # Restore original named.conf
        named_conf_file = DNS_CONFIGURATION_FOLDER + "named.conf"
        with open(named_conf_file, 'w', encoding='utf-8', newline="") as f:
            f.write(self.original_config)
            f.write("\n")

        # Upload named.conf to docker
        cp_command = "docker cp {named_conf_file} {container}:/etc/bind/{file}"\
        .format(named_conf_file=named_conf_file, container=DNS_CONTAINER_NAME, file="named.conf")
        os.system(cp_command)

        container = self.get_container()
        container.stop()

    def restart(self) -> None:
        """Method to restart the container"""
        container = self.get_container()
        container.stop()
        container.start()
