# config.py
# Configuration options of the evaluation.
# Copyright (C) 2025 Vojtěch Fiala
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.
#

class Config:
    """Available configuration settings and their validation"""

    ###########################
    # Traffic Logger Settings #
    ###########################

    # Time that the traffic-logging browser should spend on a page before quitting
    # Needs to be higher than 5 seconds since JShelter FPD takes 5 seconds to download report
    page_wait_time = 7

    # The amount of time to wait for a page load to complete before throwing an error
    time_until_timeout = 10

    # If logging fails (e.g. due to invalid DNS logs), how many times should the traffic logger
    # attempt to repeat the visit
    max_repeat_log_attempts = 3

    # Chrome version that should be used for traffic logging
    logging_browser_version = "134"

    # Whether traffic logger should launch in headless mode (no browser is shown on screen)
    headless_logging = True

    # Whether DNS validity should be checked during the logging phase
    # Should NEVER be enabled in standard situations, only for debugging purposes
    # (e.g., accessing localhost won't work without it)
    no_dns_validation_during_logging = False

    ###########################
    # Traffic Parser Settings #
    ###########################

    # Whether the Request Trees should be created to capture lower-bound metrics results
    # Should not be enabled in standard situations, only for experimental purposes
    # such as measuring how many requests were duplicated compared to upper_bound (default)
    lower_bound_trees = False

    ##############################
    # Simulation Engine Settings #
    ##############################

    # Base browser to be used during the simulation.
    # Only two valid options - "chrome" and "firefox".
    browser_type = "chrome"

    # If Google Chrome is used (and not a custom chromium-based browser),
    # this settings selects the version of Chrome to be used.
    chrome_browser_version = "134"

    # If Chromium-based custom browser (such as Avast Secure Browser or Brave Browser)
    # should be used.
    using_custom_browser = False

    # If using a custom Chromium-based browser, this is the path to its binary (.exe) file.
    # Should be in "normal" format ('/' instead of Windows's '\').
    custom_browser_binary = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

    # If using a custom Chromium-based browser, some browser (such as Avast Secure Browser)
    # require you to use a valid profile.
    # Use this setting to manually specify the correct existing profile, in '/' format.
    profile = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data"

    # If using a custom Chromium-based browser, you must use your own Chromedriver since
    # Selenium Manager was observed to not work correctly.
    # Use this setting to speicfy its path in '/' format.
    # Find Chromedriver download links here:
    # https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
    chromedriver_path = "./chromedriver_134.exe"

    # When using Firefox browser, whether to apply its default anti-tracking settings.
    # Can be used to test FF inherent content-blocking settings when no addons are specified.
    use_firefox_default_protection = True

    # List of addons to use during the simulation.
    # Addon must match the chosen browser_type, e.g. 'crx' for Chrome, 'xpi' for Firefox.
    # Evaluations described in Thesis were completed with only a single addon present
    # which was the tested tool. However, for future-proofing should work with multiple.
    tested_addons = ["ghostery_10_4_25.crx"]

    # Experiment name to be used for the current evaluation. When launching --analysis-only,
    # it needs to correspond to one of the previous experiments.
    # The log file is saved in results/ folder and it's named experiment_name + _log.json
    # The analysis results are also saved in results/ folder, named experiment_name + _results.json
    # If using Avast Secure Browser, experiment name MUST start with "avast"!! Only then!
    experiment_name = "chrome_ghostery_10_4_25"

    # Time to wait after browser is launched before accessing the simulation page.
    # The time can be used to wait for tested extensions to properly load, or to manually
    # configure them (such as enabling Ghostery or Avast Secure Browser).
    browser_initialization_time = 10

    def _validate_number_settings(self) -> bool:
        """Internal method to check whether number values are correct
        
            Returns:
                status (bool): the status whether the chosen numbers are valid.
        """
        status = True

        # Expected number values must actually be numbers
        if not  str(self.page_wait_time).isnumeric() or not\
                str(self.browser_initialization_time).isnumeric() or not\
                str(self.max_repeat_log_attempts).isnumeric() or not\
                str(self.time_until_timeout).isnumeric():
            status = False

        # Page_wait_time must be > 5
        if self.page_wait_time <= 5:
            status = False

        # Repeat log attempts must be >= 0
        if self.max_repeat_log_attempts < 0:
            status = False

        # Timeout must be >= 1
        if self.time_until_timeout < 1:
            status = False

        return status

    def validate_settings(self) -> bool:
        """Function to validate the chosen settings
            
            Returns:
                status (bool): the status whether the chosen configuration is valid.
        """
        status = True

        # Browser type supported is only chrome and firefox
        if self.browser_type not in ["chrome", "firefox"]:
            status = False

        # Using custom browser must either be true or false
        if self.using_custom_browser not in [True, False]:
            status = False

        # If using custom browser, binary path must not be empty
        if self.using_custom_browser:
            if not self.custom_browser_binary:
                status = False

        # If using Firefox and custom browser, its wrong
        if self.using_custom_browser:
            if self.browser_type == "firefox":
                status = False

        status = self._validate_number_settings()

        return status
