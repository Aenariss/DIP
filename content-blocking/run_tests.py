# run_tests.py
# Very simple script to run the tests

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

def run_all_unittests():
    """Very simple function to run the unit tests specified in folder tests/"""

    # Discover and run all tests from the tests/ folder
    # Discover all classes that inherit from unittest.TestCase
    # For each of those classes, run each method starting with test_
    loader = unittest.TestLoader()
    suite = loader.discover('tests')

    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    run_all_unittests()
