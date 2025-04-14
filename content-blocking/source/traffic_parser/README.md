## source/traffic_parser/

Traffic parser reconstructs logged request structure as directed trees. 
It also assigns the observed JShelter Fingerprinting API calls to the responsible nodes in the trees.


#### Folder contents:

Subfolders:
- ``./fp_files/`` -- Folder with configuration files for the FPD analysis, downloaded from the [JShelter repository](https://pagure.io/JShelter/webextension/blob/main/f/common/fp_config)

Files:
- ``./create_request_trees.py`` -- Controller script to parse the logs to create request trees and assign FP calls
- ``./fp_attempts.py`` -- Script to parse the FP configuration and all FP logs. Provides a dict with callers of the APIs for each request tree
- ``./request_node.py`` -- Module that defines the RequestNode class which represents a node in the request tree
- ``./request_tree.py`` -- Module that defines the RequestTree, which represents the request structure. Also contains methods to compute different statistics of the tree
