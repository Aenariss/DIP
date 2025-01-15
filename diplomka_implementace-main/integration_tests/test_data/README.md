# Test data

This folder contains source code for performing the actual integration testing. Majority of the code base as well as the overall logic has been implemented in thesis [Automatic testing of JavaScript Restrictor project](https://www.vut.cz/studenti/zav-prace/detail/129897). During the testing, retrieved values are compared against expected values, mostly using the data gathered while no extension was installed as reference. This logic has been expanded to more extensions than just *JShelter* and also their combinations.

## How does it work
Data gathered by the fingerprinting server is parsed from a JSON file an stored as an object. For one run, there are three objects at play:
- Object representing the data gathered with no extension installed.
- Object representing the data gathered with extension or combinations of extensions installed.
- Object representing the expected values defined by the developer for a run with an extension or combinations of extensions installed.

Using the `pytest` Python library, tests are performed to see if the expected data matches with the gathered data. It is up to the developer to state what should happen with the data as it passes from the client to the server while using their extension.

Every subfolder with **todays date** in the [outputs](https://github.com/kafka-mono/diplomka_implementace/blob/main/integration_tests/testing_environment/outputs) folder is scanned and each of its subfolder is considered as a single browser run. A round of testing therefore starts over every subfolder.

## Contents
- File `values_tested.py` contains the class representing attributes gathered during the fingerprint and their respective values. New attributes can be added into the class freely, as long as `values_expected.py` and `store_values.py` are modified accordingly.
- File `values_expected.py` defines the instance of objects representing values expected while using an extension or a combination of extensions gathered during the website visit. A new instance can be added - the variable representing expected values must have the same name as the list of extensions tested [here](https://github.com/kafka-mono/diplomka_implementace/blob/main/integration_tests/testing_environment/client_simulator/example_configs/README.md) seperated by the `_` symbol. For example if during the run the extensions `["JS_3", "Gh"]` were tested, the object variable representing the expected output must be called `Gh_JS_3`. Please note that the extension abbreviations representing expected values must be in alphabetical order.
- File `store_values.py` scans the fingerprint output folder for data and stores it as an object. If you are interested in gathering more data via the fingerprinting server, don't forget to edit this file to read the JSON outputs.
- File `shared_set.py` defines variables shared across a single integration testing run conducted through *pytest*.
- File `math_operations.py` defines supportive methods for testing.
- File `conftest.py` provides configuration for the *pytest* module.

## How to run
```
python3 start.py
```

## Adding your own tests
The ability to modify the objects and tests was mentioned above, however here is a short tutorial how to test the values of your own attributes. 
- Suppose you have correctly added a new method to calculate and store the attributes of a browser during visit. That includes adding it to the `tested_attributes` variable in file `env_config.py` (following the tutorial in [this file](https://github.com/kafka-mono/diplomka_implementace/blob/main/integration_tests/fingerprinting_server/fingerprint/attributes/README.md)). You can tell you have succeeded by checking if its value is contained in the JSON file the server outputs.
- Next there are three files you have to edit:
    - `store_values.py` - you need to reflect the changes made to the output JSON file. Check `read_data` function for more details.
    - `values_tested.py` - you have to add new variables to this object to reflect new attributes being gathered.
    - `values_expected.py - add expected attribute values into the objects. The attribute values are entirely up to you, you can experiment with values you know are wrong too.
- Now you can add new tests to the `pytest` module. Create a new file caled `test_...` in the `tests_definition` folder. Take any of the existing tests as reference. The `addonRun` object represents attributes gathered with an extension or a combination of extensions installed, the `noaddon` object represents the referrence visit with no extensions installed.