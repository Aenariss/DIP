## results/

Folder where the simulation and evaluation results are saved. You can analyse all ``_log.json`` files at once using ``utils/analyse_all.py`` or one by one by launching ``start.py --analysis-only`` with ``experiment_name`` specified in config.

The result files are marked with ``_results.json`` at the end and named by the experiment name.

#### Folder contents:

Subfolders:
- ``./lower_bound/`` -- Folder with results calculated from the dataset, using ``lower_bound_trees: True`` option
- ``./upper_bound/`` -- Folder with results calculated from the dataset, using ``lower_bound_trees: False`` option
