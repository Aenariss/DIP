## Content Blocking

The files in this folder are used to measure the effectivity of given content-blocking tools.  

- ``./config.json`` -- user options for the evaluation, includes browsers/extensions to test
- ``./results`` -- results of the evaluation, automatically created after starting the program
- ``./source`` -- source codes
- ``./traffic`` -- observed traffic data, automatically created after starting the program


The workflow is as follows:

1. Load all pages specified in ``pageList.txt``. Each line represents an URL to be visited.
2. The specified URLs are visited to obtain the resources downloaded for each page. For each resource, the request chain is maintained.
3. For each observed resource, a new request will be simulated for which observed DNS replies will be repeated.
4. The page with the simulated resource requests will be visited for each extension/browser specified in ``config.json``.
5. The results (containing the blocked requests) will be saved in ``results/log.txt``.

Python requirements for the evaluation are listed in ``requirements.txt``. Can be installed using ``pip install -r requirements.txt``
Also requires: Npcap (https://npcap.com/) for the DNS sniffing