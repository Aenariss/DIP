## utils/
This folder contains scripts that are not directly part of the evaluation system. 
You should **NOT** run the scripts from within the folder. They should be run from the ``content-blocking/`` folder as ``python ./utils/desired_script``.

#### Folder contents:

Subfolders:
- ``./traffic_sources/`` -- Folder containing the dataset used for the evaluation described in the thesis, also contains a list of pages used
- ``./webdrivers/`` -- Folder containing webdrivers to be used mainly with custom Chromium-based browsers. Currently contains only Chromedriver 134, as no other was used.

Files:
- ``./analyse_all.py`` -- Supporting script to run analysis for all results in the ``content-blocking/results/`` folder. Helpful when testing new metrics.
- ``./run_tests.py`` -- Script to run the implemented unit tests. Can be run from the ``content-blocking/``. Should be run with ``coverage`` module to measure code coverage. You can run it as ``coverage run ./utils/run_tests.py``. Afterwards, you can obtain coverage results with ``coverage report -m``
- ``./visualizations.py`` -- Supporting script to generate LaTeX tables with specified results from the results in the ``content-blocking/results/`` folder. Needs to be manually configured by changing the source code to print the desired metric.
