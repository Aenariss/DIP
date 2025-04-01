# test_config.py
# Test config validation functions
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

# Built-in modules
import unittest

# Custom modules
from source.config import Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def test_valid_config(self):
        """Test it's okay by default"""
        self.assertTrue(self.config.validate_settings())

    def test_validate_browser_type(self):
        """Test using invalid browser"""
        self.config.browser_type = "opera"
        self.assertFalse(self.config.validate_settings())

    def test_validate_custom_browser(self):
        """Test using invalid custom browser setting"""
        self.config.using_custom_browser = "( ͡° ͜ʖ ͡°)"
        self.assertFalse(self.config.validate_settings())

    def test_validate_custom_browser_and_binary(self):
        """Test using invalid custom binary with custom browser setting"""
        self.config.using_custom_browser = True
        self.config.custom_browser_binary = ""
        self.assertFalse(self.config.validate_settings())

    def test_validate_custom_browser_wrong(self):
        """Custom FF browser are not supported"""
        self.config.using_custom_browser = True
        self.config.browser_type = "firefox"
        self.assertFalse(self.config.validate_settings())

    def test_validate_numeric_attributes(self):
        """Test numeric attributes are actually numeric"""
        self.config.page_wait_time = "Nope"
        self.assertFalse(self.config.validate_settings())
        self.config.browser_initialization_time = "Nope"
        self.assertFalse(self.config.validate_settings())
        self.config.max_repeat_log_attempts = "Nope"
        self.assertFalse(self.config.validate_settings())
        self.config.time_until_timeout = "Nope"
        self.assertFalse(self.config.validate_settings())

    def test_validate_page_wait_time(self):
        """Test page wait time is a valid number"""
        self.config.page_wait_time = 4
        self.assertFalse(self.config.validate_settings())

    def test_validate_timeout(self):
        """Test timeout is a valid number"""
        self.config.time_until_timeout = 0
        self.assertFalse(self.config.validate_settings())
