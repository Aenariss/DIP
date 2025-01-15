# Start Visit 

## Contents
- Folder `addons` contains the packages of extensions used in testing in their respective folders - either extensions in the `.crx` format used by Google Chrome or `.xpi` format used by Mozilla Firefox. These extensions must be downloaded manually and stored inside of their respective folders. They also need to be added to the extension dictionary in `start_browser.py`.
- Folder `client_side_tests` contains files used in client-side testing - in most scenarios this will simulate the users interaction with the extension.
- `start_browser.py` sets up the browser used during the visit. More detailed information on how to install new extensions and set them up can be found inside this file.
- `start_pet.py` sets up parameters of the visit.
