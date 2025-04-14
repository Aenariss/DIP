## tests/
This folder contains unit tests to validate the implementation. The folder structure corresponds to the ``content-blocking/source`` folder and each file tests the corresponding file there.
The tests should be run using the script ``run_tests.py`` included in ``content-blocking/utils`` folder. To calculate coverage, you should use the ``coverage`` module.

#### Folder contents:

Subfolders:
- ``./analysis_engine/`` -- Folder with tests for the analysis engine
- ``./simulation_engine/`` -- Folder with tests for the simulation engine
- ``./traffic_logger/`` -- Folder with tests for the traffic logger
- ``./traffic_parser/`` -- Folder with tests for the traffic parser

Files:
- ``./test_config.py`` -- Tests of the ``content-blocking/config.py`` file
- ``./test_file_manipulation.py`` -- Tests of the ``content-blocking/source/file_manipulation.py`` file
- ``./test_setup_driver.py`` -- Tests of the ``content-blocking/source/setup_driver.py`` file
- ``./test_start.py`` -- Tests of the ``content-blocking/starts.py`` file
- ``./tests_utils.py`` -- Tests of the ``content-blocking/source/utils.py`` file
