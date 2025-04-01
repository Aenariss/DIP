# test_dns_zones.py
# Test the functions used in DNS repeat from simulation_engine
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

import unittest
from unittest.mock import patch, MagicMock

from source.simulation_engine.custom_dns_server.dns_repeater_server import DNSRepeater

class TestDNSRepeater(unittest.TestCase):

    @patch.object(DNSRepeater, "__init__")
    def setUp(self, mock_init):
        """Setup a mocked DNSRepeater"""

        mock_init.return_value = None

        # Create repeater object without init
        self.dns_repeater = DNSRepeater(None)
        self.dns_repeater.docker_client = MagicMock()
        self.dns_repeater.container = MagicMock()
        self.dns_repeater.original_config = "original_config"
        self.dns_repeater.tar_file = "zones.tar"
        self.dns_repeater.tar_path = "./" + self.dns_repeater.tar_file


        self.dns_records = {
            "example.com": {
                "www": {"A": ["192.168.0.1"], "CNAME": []}
            }
        }

    @patch.object(DNSRepeater, "_setup_container")
    @patch.object(DNSRepeater, "prepare_config")
    @patch("source.simulation_engine.custom_dns_server.dns_repeater_server.docker.from_env")
    def test_init(self, mock_docker_from_env, mock_prepare_config, mock_setup_container):
        """Test DNSRepeater init with mocks"""

        mock_docker_client = MagicMock()
        mock_docker_from_env.return_value = mock_docker_client
        mock_setup_container.return_value = "container"
        dns_repeater = DNSRepeater(self.dns_records)

        mock_docker_from_env.assert_called_once()
        self.assertEqual(dns_repeater.docker_client, mock_docker_client)
        self.assertIsNotNone(dns_repeater.container)

    @patch.object(DNSRepeater, "_setup_container")
    @patch.object(DNSRepeater, "prepare_config")
    @patch("source.simulation_engine.custom_dns_server.dns_repeater_server.docker.from_env")
    @patch("builtins.exit")
    def test_init_error(self, mock_exit, mock_docker_from_env,\
                        mock_prepare_config, mock_setup_container):
        """Test DNSRepeater init exception (two exits)"""

        mock_docker_from_env.side_effect = Exception("docker.from_env exception test")
        mock_setup_container.return_value = None
        self.assertRaises(BaseException, DNSRepeater(self.dns_records))

        # One call try: except:, second for if not self.container
        self.assertEqual(mock_exit.call_count, 2)

    @patch("os.system")
    def test_untar_file(self, mock_os_system):
        """Test untar_file method"""
        self.dns_repeater.untar_file()

        command = f"docker exec bind9 tar -xf /etc/bind/{self.dns_repeater.tar_file} -C /etc/bind"
        mock_os_system.assert_called_once_with(command)

    @patch("os.system")
    def test_copy_to_container(self, mock_os_system):
        """Test copy_to_container method"""
        file_to_copy = "test_file"
        file_location = "test_location"

        command = f"docker cp {file_to_copy} bind9:/etc/bind/{file_location}"
        self.dns_repeater.copy_to_container(file_to_copy, file_location)
        mock_os_system.assert_called_once_with(command)

    def test_create_zone_config(self):
        """Test create_zone_config works as it should"""
        expected_conf = (
            'zone "example.com" {\n'
            "       type master;\n"
            '       file "/etc/bind/example.com";\n'
            "};\n"
        )
        result = self.dns_repeater.create_zone_config("example.com")
        self.assertEqual(result, expected_conf)

    def test_generate_zonefile(self):
        """Test generate_zonefile method"""
        domain = "example.com"
        all_subdomains = {
            "www": {"A": ["192.168.0.1"]},
            "test": {"CNAME": ["another.com"]},
            "example.com": {"A": ["192.168.0.2"]}
        }

        expected_zone_file = \
            ";\n$TTL    604800\n" +\
            f"@       IN      SOA     ownnstoavoidcollisions48a.{domain}.   root.{domain}. (\n" +\
            "                 2013012110         ; Serial\n" +\
            "                     604800         ; Refresh\n" +\
            "                      86400         ; Retry\n" +\
            "                    2419200         ; Expire\n" +\
            "                     604800 )       ; Negative Cache TTL\n" +\
            ";\n" +\
            f"@       IN      NS      ownnstoavoidcollisions48a.{domain}.\n" +\
            "ownnstoavoidcollisions48a       IN      A      127.0.0.1\n" +\
            "www       IN      A       192.168.0.1\n" +\
            "test       IN      CNAME    another.com.\n" +\
            "@       IN      A       192.168.0.2\n"

        zone_file = self.dns_repeater.generate_zonefile(domain, all_subdomains)
        self.assertEqual(zone_file, expected_zone_file)

    @patch("os.path.isfile")
    @patch("builtins.open")
    @patch("os.remove")
    @patch("tarfile.open")
    @patch.object(DNSRepeater, "copy_to_container")
    def test_prepare_config(self, mock_container, mock_tarfile_open, mock_remove,\
                            mock_open, mock_isfile):
        """Test prepare_config method"""
        mock_isfile.return_value = True
        mock_file = MagicMock()
        mock_open().return_value = mock_file

        self.dns_repeater.prepare_config(self.dns_records)
        mock_open.assert_called()
        mock_tarfile_open.assert_called_once_with(self.dns_repeater.tar_path, mode="w")
        self.assertEqual(mock_container.call_count, 2)

    @patch("os.path.isfile")
    @patch("builtins.open")
    @patch("os.remove")
    @patch("tarfile.open")
    @patch.object(DNSRepeater, "generate_zonefile")
    @patch("os.listdir")
    @patch.object(DNSRepeater, "copy_to_container")
    def test_prepare_config_exception(self, mock_container, mock_listdir, mock_generate,\
                                    mock_tarfile_open, mock_remove, mock_open, mock_isfile):
        """Test prepare_config method with raised exception"""
        mock_isfile.return_value = True
        mock_listdir.return_value = ["test.com"]
        mock_file = MagicMock()
        mock_open().return_value = mock_file

        mock_generate.side_effect = Exception("Exception when preparing config test")
        self.assertRaises(BaseException, self.dns_repeater.prepare_config(self.dns_records))

        # Listdir should be called once
        mock_listdir.assert_called_once()

        # Remove should be called for "test.com"
        mock_remove.assert_called_once()

        # At the end, copy_to_contaienr should be called twice
        self.assertEqual(mock_container.call_count, 2)

    @patch.object(DNSRepeater, "get_docker_client")
    def test_find_container(self, mock_get_docker_client):
        """Test find_container method"""

        mock_docker_client = MagicMock()
        mock_get_docker_client.return_value = mock_docker_client

        # Container exists
        mock_container = MagicMock()
        mock_container.name = "bind9"
        mock_docker_client.containers.list.return_value = [mock_container]

        found_container = self.dns_repeater.find_container()

        self.assertEqual(found_container, mock_container)
        # List should be called once
        mock_docker_client.containers.list.assert_called_once_with(all=True)

        # Container doesnt exist
        mock_docker_client.containers.list.return_value = []

        found_container = self.dns_repeater.find_container()
        self.assertIsNone(found_container)
        mock_docker_client.containers.list.assert_called_with(all=True)

    @patch.object(DNSRepeater, "find_container")
    @patch.object(DNSRepeater, "get_docker_client")
    def test__setup_container(self, mock_get_docker_client, mock_find_container):
        """Test _setup_container method"""
        mock_docker_client = MagicMock()
        mock_get_docker_client.return_value = mock_docker_client

        mock_container = MagicMock()
        mock_container.name = "bind9"

        # Container exists
        mock_find_container.side_effect = [mock_container, mock_container, None,\
                                        mock_container]

        found_container = self.dns_repeater._setup_container()

        self.assertEqual(found_container, mock_container)
        mock_docker_client.containers.run.assert_not_called()

        # Container doesnt exist
        found_container = self.dns_repeater._setup_container()
        self.assertEqual(found_container, mock_container)
        mock_docker_client.containers.run.assert_called_once_with(
            image="internetsystemsconsortium/bind9:9.20",
            name="bind9",
            detach=True,
            ports={
                "53/udp": 53,
                "53/tcp": 53
            }
        )

    def test_get_container(self):
        """Test get_container method"""
        container = self.dns_repeater.get_container()
        self.assertEqual(container, self.dns_repeater.container)

    def test_get_docker_client(self):
        """Test get_docker_client method"""
        container = self.dns_repeater.get_docker_client()
        self.assertEqual(container, self.dns_repeater.docker_client)

    @patch("os.system")
    @patch.object(DNSRepeater, "get_container")
    @patch.object(DNSRepeater, "restart")
    @patch.object(DNSRepeater, "untar_file")
    def test_start(self, mock_untar, mock_restart, mock_get_container, mock_os_system):
        """Test the start method"""

        mock_container = MagicMock()
        mock_get_container.return_value = mock_container

        self.dns_repeater.start()

        mock_os_system.assert_called_once_with(
            'powershell -NoProfile -ExecutionPolicy Bypass -Command "' +\
            'Set-DnsClientServerAddress -InterfaceAlias \'Ethernet\' -ServerAddresses 127.0.0.1"')
        mock_container.start.assert_called_once()
        mock_untar.assert_called_once()
        mock_restart.assert_called_once()

    @patch("os.system")
    @patch.object(DNSRepeater, "get_container")
    @patch("os.listdir")
    @patch("os.remove")
    @patch("os.path.isfile")
    @patch.object(DNSRepeater, "copy_to_container")
    @patch("builtins.open")
    def test_stop(self, mock_open, mock_copy_to_container, mock_isfile, mock_os_remove,\
                   mock_os_listdir, mock_get_container, mock_os_system):
        """Test the stop method"""

        mock_container = MagicMock()
        mock_get_container.return_value = mock_container
        mock_os_listdir.return_value = ["test_file"]
        mock_isfile.return_value = True

        self.dns_repeater.stop()

        mock_os_system.assert_any_call(
            'powershell -NoProfile -ExecutionPolicy Bypass -Command' +\
            ' "Set-DnsClientServerAddress -InterfaceAlias \"Ethernet\" -ResetServerAddresses"')

        # os remove only once for the singular test_file
        mock_os_remove.assert_called_once()
        mock_os_system.assert_any_call("docker exec bind9 rm -rf /etc/bind/*")
        self.assertEqual(mock_os_system.call_count, 2)
        mock_copy_to_container.assert_called_once()
        mock_container.stop.assert_called_once()

    @patch.object(DNSRepeater, "get_container")
    @patch("time.sleep")
    def test_restart(self, mock_sleep, mock_get_container):
        """Test the restart method"""

        mock_container = MagicMock()
        mock_get_container.return_value = mock_container

        self.dns_repeater.restart()
        mock_container.stop.assert_called_once()
        mock_container.start.assert_called_once()
