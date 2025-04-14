## source/simulation_engine/custom_dns_server

Setup the custom BIND 9 DNS server to repeat DNS responses.

After the evaluation is over, configuration is restored to default and host system DNS configuration is reset.

#### Folder contents:

Subfolders:
- ``./server_configuration/`` -- Folder configuration of the DNS server. Custom zone files are also generated here
    - ``./server_configuration/named.conf`` -- configuration of the DNS server. Generated zone files are included inside.

Files:
- ``./dns_repeater_server.py`` -- Setups the Docker container with BIND 9 server. Uploads the configuration and zone files. Configures the host system to use the custom server running on address 127.0.0.1.
