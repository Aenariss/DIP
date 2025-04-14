## addons/chrome

Contains extensions for the Chrome browser.

#### Folder contents:

Files:
- ``./adblock_plus_4_15_0.crx`` -- Adblock Plus version 4.15.0
- ``./ghostery_10_4_25.crx`` -- Ghostery version 10.4.25
- ``./jshelter_0_19_custom_fpd.crx`` -- JShelter version 0.19, edited to automatically start fingerprint detection on page access
- ``./jshelter_0_20_custom_fpd_doesnt_work.crx`` -- JShelter version 0.20 which doesnt correctly work in Selenium
- ``./privacy_badger_2025_1_29.crx`` -- Privacy Badger version 2025.1.29
- ``./ublock_origin_lite_2025_3_2_1298.crx`` -- uBlock Origin Lite version 2025.3.2.1298


#### Edited JShelter:

If you want to check the source code, simply open the archive for example with WinRar.

The JShelter edited source code is explicitly listed in another [repository](https://github.com/Aenariss/jshelter-fpd-test), which is used to test the 0.19 and 0.20 logging functionality. The custom versions are included as a folder which contains the original cloned repository with a custom commit that introduced the FPD changes.

JShelter was modified to have the option for tracking calling script allowed by default. Default shields are disabled by default. All custom edits are marked by a commentary ``// 2025 custom edit`` or ``// custom 2025 edit``. My name (Vojtěch Fiala) is also included as one of the authors in the edited files. The purpose of the edits is basically to always enable JShelter FPD. Other edits include a custom listener that downloads the FPD report 5 seconds after a page was accessed.

Edited files are:
- ``document_start.js`` -> added listener to log FPD report in console
- ``fp_level.js`` -> created new listener for when a new page has been opened. Launches the custom caller tracking function.
- ``fp_report_custom.js`` -> obtains the callers and downloads them as json.
- ``level_cache.js`` -> sets trackCallers to always true. Always assigns FPD wrappers.
- ``levels.js`` -> sets const fpdOn to true. Sets the protection level to 0.
- ``service_worker.js`` -> includes fp_report_custom.js.
- ``manifest.json`` -> added permission for downloads.
