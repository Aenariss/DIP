## source/
This folder contains source code of the evaluation. Each subfolder contains parts of that part of the evaluation. The files in this folder are used in multiple parts of the evaluation.
The code should be run using the script ``start.py`` in the folder above.

The evaluation proceeds as follows:

1. Data is logged using traffic logger. It logs network events, DNS responses and fingerprinting activity. JShelter FingerPrinting Detector is used to log fingerprinting activity.
2. Data is parsed using traffic parser. It creates directed request trees that facilitate transitive evaluation of request blocking. Each node in the tree represents an observed request. The nodes are assigned the corresponding fingerprinting attempts.
3. Blocking simulation is provided by the simulation engine. it creates a custom webserver which loads the observed resources. The simulation engine logs which of the requests are blocked by the tested content-blocking tool and logs it. During the simulation, observed DNS responses are repeated by a custom DNS server and Firewall rules are used to prevent unnecessary network traffic from leaving the device.
4. Simulation results are analyzed using the analysis engine. It uses simulation logs and request trees to analyse how many requests in the trees would a given tool block. Also counts transitive properties and other metrics.

#### Folder contents:

Subfolders:
- ``./analysis_engine/`` -- Folder with code of the analysis engine
- ``./simulation_engine/`` -- Folder with code of the simulation engine
- ``./traffic_logger/`` -- Folder with code of the traffic logger
- ``./traffic_parser/`` -- Folder with code of the traffic parser

Files:
- ``./constants.py`` -- Specifies constants and paths. Unifies them in one place and then uses them throughout the evaluation.
- ``./file_manipulation.py`` -- Manipulates files, such as loading and saving JSONs
- ``./setup_driver.py`` -- Prepares a Selenium driver for both the traffic logging and the simulation, depending on the specified configuration and arguments
- ``./utils.py`` -- Contains utility functions that are used in multiple files
