## source/simulation_engine/

Repeats the observed requests and their DNS responses. Launches a custom BIND 9 DNS server that generates zone files from the DNS logs. Also launches a custom web server which is visited with a content-blocking tool loaded to log what requests it blocks.

The blocking results are saved in the ``results/`` folder. They are named as the specified ``experiment_name`` defined in ``config.py``, with ``_log.json`` appended at the end.

#### Folder contents:

Subfolders:
- ``./custom_dns_server/`` -- Folder with the code to setup the custom DNS server
- ``./simulation_webserver/`` -- Folder with HTML code of the simulation web server
    - ``./simulation_webserver/index.html`` -- defines the index page (which is the only page used), together with javascript functions to repeat the requests. Uses fetch() to load them, which might limit functionality of heuristic-based tools.

Files:
- ``./firewall.py`` -- Defines the functions that use PowerShell commands to setup firewall rules that block outgoing HTTP and HTTPS requests
- ``./simulation_server_setup.py`` -- Starts the simulation web server
- ``./visit_test_server.py`` -- Script that visits the web server and obtains blocking results
