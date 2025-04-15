## Content Blocking

This program works only on **Microsoft Windows** because of several internal Windows utilities it uses.

Please, read this file, mainly the **IMPORTANT** section, before launching anything.

This folder contains everything that was used to evaluate the results, test the implementation and visualize the results.
Launch all files mentioned from inside the root folder only -> you should be in /DIP/content-blocking!
Please, do not remove any ``.empty`` file you find.

Requirements to run:
- Docker (Docker Destop) -- https://docs.docker.com/desktop/setup/install/windows-install/
- Python -- https://www.python.org/downloads/
- Npcap -- https://npcap.com/
- specified python modules -- listed in ``requirements.txt``. Can be installed using ``pip install -r requirements.txt``
- non-empty ``page_list.txt`` file -- needs to be populated with URL addresses in format http(s)://page -> e.g. https://www.vut.cz/

How to setup an environment:
- Before launching anything, make sure all requirements are satisfied.
- Launch python as admin when running simulation:
    - You can allow "sudo" command in Windows settings => System > For Developers > Enable sudo
    - Afterwards, run all simulation commands as ``sudo command``
- In case you are launching for the first time, you need to download the docker image (for custom DNS server): -> 
    - ``docker pull internetsystemsconsortium/bind9:9.20``
- Disable IPv6 at the network adapter (Control panel -> Network -> View network status -> Change adapter settings -> Properties -> ipv6)
- Make sure to correctly configure your network adapter name in ``./source/constants``, otherwise a DNS server cannot be assigned

All examples that are started with ``sudo`` **MUST** be run with sudo since they use windows utilities that require admin privileges, such as Firewall and changing default DNS server.

How to launch:
- ``python ./start.py --load-only`` -- loads traffic on all pages specified in ``page_list.txt`` and nothing else.
- ``sudo python ./start.py --load`` -- loads traffic on all pages specified in ``page_list.txt`` and afterwards uses it as a basis for simulation and evaluation.
- ``sudo python ./start.py --load --compact`` -- can also be used with --load-only -> loads traffic in compact format, instead of saving the entire callstack, saves only the first valid parent which the traffic parser would select anyway.
- ``sudo python ./start.py`` -- loads already logged traffic which is saved in ./traffic/ folder and start the simulation followed by evaluation.
- ``sudo python ./start.py --simulation-only`` -- only starts the simulation on the logged traffic data.
- ``python ./start.py --analysis-only`` -- only starts the analysis on the blocking simulation results.

Support scripts:
- ``python ./utils/visualizations.py`` -- support script to print the results in latex tables. Needs to be manually configured to print the required data.
- ``python ./utils/analyse_all.py`` -- support script to run the analysis of existing simulation results. Runs it for all existing files in the ./results/ folder that ends with ``_log.json``

Tests:
You should run tests with the obtained folder content, e.g. traffic/ folder exists etc.
- ``python ./utils/run_tests.py`` -- run the tests
- ``coverage run ./utils/run_tests.py`` -- if coverage module is installed, this command runs the tests and computes the coverage. Takes a few seconds to finish, do not be scared by the error outputs. A .coverage results file is stored in the root folder.
- ``coverage report -m`` -- if coverage module is installed and ``coverage run`` was used, this command parses the results and outputs the logged coverage.

#### IMPORTANT
- When launching the file with any load options -- that is ``--load`` or ``--load-only``, **ALL RESULTS IN ./traffic/ FOLDER ARE DELETED**.
- Make sure to always give tested addons enough time to load (at least 10 sec, ``config/`` the ``browser_initialization_time`` property)
- Sometimes when launching selenium (may happen when launching for the first time in PC session, subsequent runs are fine), it may take too long to load and thus
skip enabling devtools. In such cases, please restart the program and it should work as intended. 
- JShelter FPD sometimes has a race condition which causes fingerprinting to not work on some pages. 
- When saving the results, if a result with a given name already exists, it will be overwritten.
- To get a list of pages to populate the page_list.txt, try Tranco (not ideal, contains CDNs, DNS servers...) or https://dataforseo.com/free-seo-stats/top-1000-websites or some other source.
- After stopping the custom DNS server, DNS settings are reset -> it is set to automatic DHCP assignment. This means you lose your own settings.
- If you manually stop the program during simulation, it may not reset your DNS settings or delete the added firewall rules. An exception handler should solve this, but if you quit during the handling, it does not work.
- In case something goes wrong during simulation (for example, you quit it wrong), the docker DNS server may get corrupted and not start properly -> in that case, just create a new image.

The example workflow is as follows:
1. Specify your desired pages in ``page_list.txt``. Each line represents an URL to be visited.
2. Configure your ``./config.py`` file by following the instructions written inside. 
3. Run ``python ./start.py --load-only``. By default, it runs in headless mode, so you should not be overly disrupted. On average, it takes 25 seconds per page. If you specified a lot of pages, this might take a while.
4. Check your ``./config.py`` if your desired extension or browser to test is specified properly. Also don't forget to write an experiment name. If you wish to calculate the lower-bound approach, set the ``lower_bound_trees`` option to True.
5. After traffic was succesfully collected, run ``python ./start.py --simulation-only``. Depending on the numbers of requests tested and the chosen browser, this may take a while.
6. After your simulation results are saved in the ``./results/`` folder, run ``python ./start.py --analysis-only`` to obtain the results. Don't forget to use the same experiment name as for simulation!
7. Wait for the analysis to conclude and check your results in the ``./results`` folder.

Problems and Solutions:
- MakError with DNS server configuration during simulation -- - Make sure to correctly configure your network adapter name in ``./source/constants``, otherwise a DNS server cannot be assigned.
- DNS observation during traffic logging sometimes fails, caused by Scapy as it saves each packet real time. It may thus miss some. During traffic logging, it is recommended to not use the computer to avoid unnecessary DNS traffic.
Can be partially solved by setting higher number of repeat attempts in config.
- JShelter FPD sometimes has a race condition which causes fingerprinting to not work on some pages. 
- A DNS server may fail if some strange, yet unsolved DNS situation happened. Please, always first run test with pure chrome browser (since firefox does not log errors). If something went wrong, you will see err::NAME_NOT_RESOLVED in result logs.
In such cases, the simplest solution is to collect traffic again, preferably from different pages.
- All paths need to be with '/' instead of Windows '\\' (config)
- Experiments with "avast secure browser" need to have experiment name starting with "avast" -- only then the profile is correctly loaded
- Traffic logging requires valid page address (http(s)://my.example.com, does not work for localhost etc. Requires at least one dot. Unless config.debug is specified)
- Not everything in the config is validated since there are many possible options (which may even be expanded in the future), so please do not change what you do not understand to not break the program.
- If you get an error with analysis-only, check your specified browser type matches the experiment logs (firefox experiment can only work with firefox logs and chrome vice-versa)
- The addresses in page_list.txt need to have "http(s)://" prefix to correctly open in Selenium! 

#### Folder contents:

Subfolders:
- ``./addons/`` -- Folder with browser extensions to test and custom extensions used during logging and simulation
- ``./results/`` -- folder with results of the evaluation, automatically created after starting the program. All results are saved there. The files are named with the defined experiment name.
    Simulation logs are appended with ``_log.json`` suffix. Analysis results are appended ``_results.json`` suffix.
- ``./source/`` -- source codes. Files used across the evaluation are in this folder. The subfolders concern each part of the evaluation.
- ``./tests/`` -- folder with unit tests to validate the implementation. Split into the same structure as ``./source/``, with each file testing the corresponding source file.
- ``./traffic/`` -- observed traffic data, automatically created after starting the program if doesn't exist. You should **NOT** put anything there other than traffic files in the pre-configured format ([1-9][0-9]*_(network|dns|fp).json)
- ``./utils/`` -- Folder containing additional helpful data, such as a script to run the tests, script to run the analysis of all results in ``./results`` folder and script to print the data from results into tables.

Files:
- ``./config.py`` -- user options for the evaluation, includes browsers/extensions to test
- ``./starts.py`` -- The main script which is used to run almost everything else
- ``./page_list.txt`` -- The file containing the pages to be visited during the traffic logging process to create a dataset. The format has to be one address per line. The addresses MUST start with http(s)://
