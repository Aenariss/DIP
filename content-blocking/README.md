## Content Blocking

This program works only on **Microsoft Windows** because of some internal Windows stuff it uses.

Please, read the **IMPORTANT** section in this file before launching anything.

The files in this folder are used to measure the effectivity of given content-blocking tools.  

- ``./source/config.py`` -- user options for the evaluation, includes browsers/extensions to test
- ``./results`` -- results of the evaluation, automatically created after starting the program
- ``./source`` -- source codes
- ``./source/fp_files`` -- JShelter files used for FPD purposes
- ``./traffic`` -- observed traffic data, automatically created after starting the program

Requirements to run:
- Docker (Docker Destop) -- https://docs.docker.com/desktop/setup/install/windows-install/
- Python -- https://www.python.org/downloads/
- Npcap -- https://npcap.com/
- specified python modules -- listed in ``requirements.txt``. Can be installed using ``pip install -r requirements.txt``
- non-empty ``page_list.txt`` file -- needs to be populated with URL addresses in format protocol://page -> e.g. https://www.vut.cz/

How to start in case of manual launch:
- Launch all files mentioned from inside the root folder only -> you should be in ./DIP/content-blocking
- Before launching anything, make sure all requirements are satisfied.
- Launch python as admin:
    - You can allow "sudo" command in Windows settings => System > For Developers > Enable sudo
    - Afterwards, run all mentioned commands as ``sudo command``
- In case you are launching for the first time, you need to setup docker (for custom DNS server): -> 
    - ``docker pull internetsystemsconsortium/bind9:9.20``

#### IMPORTANT
When launching the file with any load options -- that is ``--load`` or ``--load-only``, **ALL RESULTS IN ./traffic/ FOLDER ARE DELETED**.

Sometimes when launching selenium (usually when launching for the first time in PC session), it may take too long to load and thus
skip enabling devtools. In such cases, please restart the program and it should work as intended. 

JShelter FPD sometimes has a race condition which causes fingerprinting to not work on some pages. 

When saving the results, if a result with a given name already exists, it will be overwritten.

Windows may not work with custom DNS server, it prefers ipv6 dns resolution -> disable ipv6 in adapter options: control panel -> Network -> View network status -> Change adapter settings -> Properties -> ipv6

To get a list of pages to populate the page_list.txt, try Tranco (not ideal, contains CDNs, DNS servers...) or https://dataforseo.com/free-seo-stats/top-1000-websites

After stopping the custom DNS server, DNS settings are reset -> it is set to automatic DHCP assignment. This means you lose your own settings.

- There are three options how to launch the evaluation:
    - use ``python ./start.py --load-only`` loads traffic on all pages specified in ``page_list.txt`` and nothing else.
    - use ``python ./start.py --load`` loads traffic on all pages specified in ``page_list.txt`` and afterwards uses it as a basis for evaluation.
    - use ``python ./start.py --load --compact`` (can also be used with --load-only) to lessen the space the traffic logs take.
    - use ``python ./start.py`` loads already logged traffic which is saved in ./traffic/ folder.



The workflow is as follows:

1. Load all pages specified in ``pageList.txt``. Each line represents an URL to be visited.
2. The specified URLs are visited to obtain the resources downloaded for each page. For each resource, the request chain is replicated. During visitation, DNS sniffer is active and logs DNS traffic.
3. For each observed resource, a new request will be simulated for which observed DNS replies will be repeated.
4. The page with the simulated resource requests will be visited for each extension/browser specified in ``config.json``.
5. The results of the simulation will be saved in ``results/`` folder.

Problems:
DNS observation during traffic logging sometimes fails, cause unknown (Scapy-caused issue). During traffic logging, it is recommended to not use the computer to avoid unnecessary DNS traffic.
Can be partially solved by setting higher number of repeat attempts in config.

JShelter FPD sometimes has a race condition which causes fingerprinting to not work on some pages. 

Sometimes, DNS server fails since some unexpected DNS situations may occur. PLease, always first run test with pure chrome browser (since firefox does not log errors). If something went wrong, you will see err::NAME_NOT_RESOLVED in result logs.
In such cases, the simplest solution is to collect traffic again.

All paths need to be with '/' instead of Windows '\' (config)

Experiments with "avast secure browser" need to have experiment name starting with "avast" -- only then the profile is correctly loaded

Tested addons needs whole name of the file

Traffic logging requires valid page address (http(s)://my.example.com, does not work for localhost etc. Requires at least one dot. Unless config.ddebug is specified)

Not everything in the config is validated since there are many possible options (which may even be expanded in the future), so please do not change what you do not understand to not break the program.

If you get an error with analysis-only, check your specified browser type matches the experiment logs (firefox experiment can only work with firefox logs and chrome vice-versa)