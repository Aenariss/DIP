## source/traffic_logger/
Contains code of the traffic logger which is reponsible for the dataset creation.
Traffic logging includes collection of DNS logs using the Scapy module. Network logs are collected from the selenium driver using the built-in Chrome DevTools Protocol support. Fingerprinting activity is detected using a custom version of JShelter 0.19 which I modified. 

The JShelter version is located in /addons/chrome/jshelter_0_19_custom_fpd. The changes are described in custom [repository](https://github.com/Aenariss/jshelter-fpd-test)

#### Folder contents:

Files:
- ``./dns_observer.py`` -- Code for the DNS observed built using Scapy. Logs all A and CNAME responses and creates artifical records to maintain CNAME chains
- ``./network_logs_loader.py`` -- Script to obtain and parse network logs collected from the simulated browser
- ``./traffic_loader.py`` -- Script that drives the data collection. Also validates the DNS logs to ensure no domain is missing
