## Content Blocking

This program works only on **Microsoft Windows** because of several internal Windows utilities it uses.

Please, read this file, mainly the **IMPORTANT** section, before launching anything.

This folder contains everything that was used to evaluate the results, test the implementation and visualize the results.
Launch all files mentioned from inside the root folder only -> you should be in /DIP/content-blocking!

The folders present are:
- ``./addons/`` -- Folder with browser extensions to test
    - ``./addons/chrome/`` -- Extensions in the ``.crx`` format for Chromium-based browsers. Includes the custom edited JShelter version in the ``.crx`` format. 
    Each file I edited has me added as an editor and the custom code is marked with ``// 2025 custom edit`` or ``// custom 2025 edit``. Source code in folders is available here: https://github.com/Aenariss/jshelter-fpd-test
    - ``./addons/firefox/`` -- Extensions in the ``.xpi`` format for the Firefox browser
    - ``./addons/firefox_resource_logger/`` -- Custom extension to log the blocked (allowed) requests in Firefox.
- ``./results/`` -- folder with results of the evaluation, automatically created after starting the program. All results are saved there. The files are named with the selected experiment name.
    Simulation logs are appended with ``_log.json`` suffix. Analysis results are appended ``_results.json`` suffix.
- ``./source/`` -- source codes. Files used across the evaluation are in this folder. The subfolders concern each part of the evaluation.
    - ``./source/traffic_logger/`` --  First part used to log the traffic data -- DNS requests, network requests and fingerprinting activity
    - ``./source/traffic_parser/`` -- Second part which parses the logged traffic, creates request trees and assigns fingerprinting attempts
        - ``./source/traffic_parser/fp_files/`` -- FP Groups and Wrappers obtained from the official JShelter repository https://pagure.io/JShelter/webextension
    - ``./source/simulation_engine/``-- Third part which simulates the request blocking by setting up a custom web server which re-requests all the observed resources.
        - ``./source/simulation_engine/custom_dns_server`` -- Folder with code and data for the custom DNS BIND 9 server. Contains generated zone files.
        - ``./source/simulation_engine/simulation_webserver`` -- Contains the index page of the custom web server, which includes the javascript code to fetch the resources.
    - ``./source/analysis_engine/`` -- Fourth part used to parse the simulation logs and propagate the blocking into the request trees. The trees are then analyzed and metrics are calculated.
- ``./tests/`` -- folder with unit tests to validate the implementation. Split into the same structure as ``./source/``, with each file testing the corresponding source file.
- ``./traffic/`` -- observed traffic data, automatically created after starting the program
- ``./utils/`` -- Folder containing additional helpful data, such as a script to run the tests, script to run the analysis of all results in ``./results`` folder and script to print the data from results into tables.
    - ``./utils/traffic_sources/`` -- contains .zip with the traffic data used for the evaluations and comparison described in the thesis, coupled with a list of 1000 webpages the data was collected from.
    - ``./utils/webdrivers/`` -- contains webdrivers to be used with custom Chromium-based browser. Currently contains only Chromedriver 134 as no other was necessary.

The files in this folder are:
- ``./config.py`` -- user options for the evaluation, includes browsers/extensions to test
- ``./starts.py`` -- The main script which is used to run almost everything else
- ``./page_list.txt`` -- The file containing the pages to be visited during the traffic logging process to create a dataset. The format has to be one address per line. The addresses MUST start with http(s)://

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
    - Afterwards, run all mentioned commands as ``sudo command``
- In case you are launching for the first time, you need to setup docker (for custom DNS server): -> 
    - ``docker pull internetsystemsconsortium/bind9:9.20``
- Disable IPv6 at the network adapter (Control panel -> Network -> View network status -> Change adapter settings -> Properties -> ipv6)

How to launch:
- ``python ./start.py --load-only`` -- loads traffic on all pages specified in ``page_list.txt`` and nothing else.
- ``python ./start.py --load`` -- loads traffic on all pages specified in ``page_list.txt`` and afterwards uses it as a basis for simulation and evaluation.
- ``python ./start.py --load --compact`` -- can also be used with --load-only -- loads traffic in compact format, instead of saving the entire callstack, saves only the first valid parent which the traffic parser would select anyway.
- ``python ./start.py`` -- loads already logged traffic which is saved in ./traffic/ folder and start the simulation followed by evaluation.
- ``sudo python ./start.py --simulation-only`` -- only starts the simulation on the logged traffic data. **MUST** be run with sudo since it uses windows utilities that require admin privileges, such as Firewall and changing default DNS server.

Support scripts:
- ``python ./utils/visualizations.py`` -- support script to print the results in latex tables. Needs to be manually configured to print the required data.
- ``python ./utils/analyse_all.py`` -- support script to run the analysis of existing simulation results. Runs it for all existing files in the ./results/ folder that ends with ``_log.json``

Tests:
- ``python ./utils/run_tests.py`` -- run the tests
- ``coverage run ./utils/run_tests.py`` -- if coverage module is installed, this command runs the tests and computes the coverage. Takes a few seconds to finish, do not be scared by the error outputs. A .coverage results file is stored in the root folder.
- ``coverage report -m`` -- if coverage module is installed and ``coverage run`` was used, this command parses the results and outputs the logged coverage.


#### IMPORTANT
- When launching the file with any load options -- that is ``--load`` or ``--load-only``, **ALL RESULTS IN ./traffic/ FOLDER ARE DELETED**.
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
- DNS observation during traffic logging sometimes fails, caused by Scapy as it saves each packet real time. It may thus miss some. During traffic logging, it is recommended to not use the computer to avoid unnecessary DNS traffic.
Can be partially solved by setting higher number of repeat attempts in config.
- JShelter FPD sometimes has a race condition which causes fingerprinting to not work on some pages. 
- A DNS server may fail if some strange, yet unsolved DNS situation happened. PLease, always first run test with pure chrome browser (since firefox does not log errors). If something went wrong, you will see err::NAME_NOT_RESOLVED in result logs.
In such cases, the simplest solution is to collect traffic again, preferably from different pages.
- All paths need to be with '/' instead of Windows '\' (config)
- Experiments with "avast secure browser" need to have experiment name starting with "avast" -- only then the profile is correctly loaded
- Traffic logging requires valid page address (http(s)://my.example.com, does not work for localhost etc. Requires at least one dot. Unless config.debug is specified)
- Not everything in the config is validated since there are many possible options (which may even be expanded in the future), so please do not change what you do not understand to not break the program.
- If you get an error with analysis-only, check your specified browser type matches the experiment logs (firefox experiment can only work with firefox logs and chrome vice-versa)
- The addresses in page_list.txt need to have "http(s)://" prefix to correctly open in Selenium! 
