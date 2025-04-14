## source/analysis_engine/

Code that launches the analysis and computes defined metrics.

Some of the metrics are computed basedd on the statistical functions defined as part of the RequestTree class, specified in ``source/traffic_parser/request_tree.py``.

Depending on the specified ``experiment_name`` in ``config.py``, loads the corresponding log file (needs to have ``_log.json`` suffix, as created by the simulation engine) and saves the results in ``results/`` folder as a file named the ``experiment_name`` with ``_results.json`` appended.

#### Folder contents:

Files:
- ``./analysis_utils.py`` -- Utils used during the analysis
- ``./analysis.py`` -- Main analysis driver file, uses the other files to compute metrics from the log file which has to be in the ``results/`` folder
- ``./experimental_analysis.py`` -- Computes experimental metrics
- ``./fingerprinting_analysis.py`` -- Computes fingerprinting metrics
- ``./requests_analysis.py`` -- Computes request metrics
