## Content Blocking

The files in this folder are used to measure the effectivity of given content-blocking tools.  

- ``./config.json`` -- user options for the evaluation, includes browsers/extensions to test
- ``./results`` -- results of the evaluation, automatically created after starting the program
- ``./scripts`` -- Powershell scripts to control OS-specific functionalities
- ``./source`` -- source codes
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
- ~~In case you are launching for the first time, you need to setup docker (for custom DNS server): -> ~~
    - ``cd custom_dns_server``
    - ``docker build -t dns_server . ``
    - ``docker run -it --dns=127.0.0.1  -p 53:53/udp dns_server``
    - ``Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses 192.168.1.242`` 
    - ``Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ResetServerAddresses`` to fix

- There are two options how to launch the evaluation:
    - use ``python ./start.py --load`` loads traffic on all pages specified in ``page_list.txt`` and afterwards uses it as a basis for evaluation.
    - use ``python ./start.py`` loads already logged traffic which is saved in ./traffic/ folder.


The workflow is as follows:

1. Load all pages specified in ``pageList.txt``. Each line represents an URL to be visited.
2. The specified URLs are visited to obtain the resources downloaded for each page. For each resource, the request chain is maintained.
3. For each observed resource, a new request will be simulated for which observed DNS replies will be repeated.
4. The page with the simulated resource requests will be visited for each extension/browser specified in ``config.json``.
5. The results (containing the blocked requests) will be saved in ``results/log.txt``.
