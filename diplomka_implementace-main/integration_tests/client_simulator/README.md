# Client simulator

The visiting of a fingerprinting server is simulated through visits using **Selenium**. The whole process consists of these steps:
- First the program gathers the run parameters. These parameters are stored in configuration files further described inside the `example_coinfigs` folder.
- Next the browser driver is set up. This could be either Mozilla Firefox or Google Chrome in several different versions. Set up includes downloading the browser drivers using **Selenium Manager**, the instalation of extensions, setting up Firefox profile, editing the browsers options so data could be gathered and activating the extension if the extension requires it. In the case of **JShelter**, the tested level is selected in the extensions options. 
- If stated in the client configuration files, the client-side testing is performed. These are the test that could not be implemented server-side, but could be a relevant source of information for developers.
- After that the client simulates a visit to the fingerprinting server running inside of the container.
- All the steps mentioned are done for every list of browser-extension combination inside the client configuration file.

## Contents
- Folder `start_visit` contains source code for simulating the clients visit.
- Folder `example_configs` contains configuration files that can be used during tesing.
- File `start.py` is used as an entrypoint of the simulation.

## How to run
Run the client simulation using the command:
```
python3 start.py client_configuration.json server_configuration.json
```
Note that the client is deployed immediately after running the Docker container without requiring any user input.