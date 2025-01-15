# Integration testing

This folder contains the code base for integration testing of privacy enhancing extensions. Much of the code base was taken from the [**PETInspector project**](https://github.com/tadatitam/pet-inspector) conducted as part of a 2019 paper called [Evaluating Anti-Fingerprinting Privacy Enhancing Technologies](https://www1.icsi.berkeley.edu/~mct/pubs/www19.pdf). The fingerprinting server was originally created by Pierre Laperdrix in 2016 as [Fingerprint Central](https://github.com/plaperdr/fp-central). Analysis engine was completely omitted in the thesis and instead replaced by a new mechanism designed to test the expected results against retrieved results. This mechanism is based on the original integration tests implemented in thesis [Automatic testing of JavaScript Restrictor project](https://www.vut.cz/studenti/zav-prace/detail/129897). The original project also allowed users to test in different OS settings, although by the time of writing this thesis, this feature no longer worked at all. Due to this and the nature of Docker virtualization, it has been removed entirely. A **Dockerfile** is also included in this folder.

The original code base has been heavily modified to take advantage of a feature implemented by [Selenium](https://www.selenium.dev) in 2022 called [Selenium Manager](https://www.selenium.dev/documentation/selenium_manager/). Some of the new features include:
- The ability to perform tests with multiple extensions installed. This includes different combinations of available extensions. 
- Testing using different available browser versions for both Google Chrome and Mozilla Firefox.
- Several new techniques intended to test the extension's ability to block or alter data retrieved by the server.
- Performing client-side testing.


Please note that this tool does not serve as an evaluation of a browsers extension's ability to protect against fingerprinting. This tool was designed as a way for users and developers to see and analyze the extension's behavior in a controlled, deterministic and transparent settings while also giving them the ability to see how multiple installed extensions affect each other and their outputs. It does not accurately represent the reality of fingerprinting servers, it only simulates their behavior.

## Contents
Integration testing consists of three main parts:
- The emulation of a user visiting a site that creates users browser fingerprint. This user could be using either Google Chrome or Mozilla Firefox to access said webpage. They could have no extension or a combination of extensions installed. Contained in `client_simulator`.
- A server implementing known techniques used to calculate users fingerprint. The server runs continuously inside the container and gathers data once the simulated client visits its webpage. This data is stored into a JSON file. Contained in `fingerprinting_server`.
- After relevant data is gathered by the fingerprinting server and stored in s JSON file, it is compared against the expected results. Contained in `test_data`.
- `outputs` contains attribute data calculated by the server as well as the results of integration testing.

Script `start_testing.sh` is run immediately after creating and executing the container from a Docker image. By default the server is deployed and its outputs are logged into the `server.log` file. The client is initiated using the command:
```
python3 start.py ./example_configs/client.json ./example_configs/server.json
```
The configuration files to be used can be changed. 

## How to configure the tests
See [`client_simulator/example_configs`](https://github.com/kafka-mono/diplomka_implementace/tree/main/integration_tests/client_simulator/example_configs) for more information.