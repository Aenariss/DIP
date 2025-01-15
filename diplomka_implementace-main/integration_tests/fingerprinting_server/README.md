# Fingerprinting server
This folder contains the code base to deploy a *Flask* server serving as a potential fingerprinting risk. The server gathers visiting user's data and stores them inside a JSON file. The server is deployed immediately after the container starts. From then on it runs continuously till the container is stopped.

## Static folder
This folder contains data needed to create the fingerprinting website, including *CSS selectors*, *fonts*, *images* and *scripts*. If you wish to edit the look, layout or JavaScript of the website run by fingerprinting server, you can do so from here. If you are interested in modifying the website at all, you should pay special attention to the `/static/js/clientAPI.js` file.

## Templates folder
This folder similarly contains *HTML* files used by the site.

## Fingerprint folder
Used to gather users data collected during their visit. All the fingerprint logic is stored here.

## Outputs folder
This folder stores all JSON data gathered by the server. The server creates subfolders named after the timestamp of the first run performed with no extensions installed and the name of browser used - that means a run with "None" set as extensions in its name. When a visit with no extensions installed occurs, a new subfolder is created. Due to this, you must *ALWAYS* perform a "None" run first on the client's side in order to store data correctly.

## `env_config.py` file
This file contains the environment configuration of the server. It also lists all the fingerprinting techniquest that will be used after the servers deployment in `tested_attributes`. If you wish not to test an attribute, you can simply comment it out. If you add a new testing attribute, you must also add its name to the `tested_attributes` inside this file.

---
### How to run
You can deploy the server using this command:
```
python3 run.py
```
Note that it is deployed defaultly through the `start_testing.py` script after running the container.