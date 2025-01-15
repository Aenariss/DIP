#
#  Copyright (C) 2021  Martin Bednar
#  Copyright (C) 2024  Jana Petranova
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import pytest
from shared_set import get_shared_addonRun
	
from math_operations import is_in_accuracy, calc_distance

## Test accuracy of the latitude and longitude properties in meters.

def test_accuracy(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.accuracy is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.accuracy['value'] == 'REAL VALUE':
        if addonRun.geolocation.accuracy == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.accuracy == noaddon.geolocation.accuracy
        else:
            if expected.geolocation.accuracy['accuracy'] == 'EXACTLY':                
                # x is real position (position returned without JShelter)
                # y should be real position too (position returned with JShelter level 0)
                #
                # It is clear that x and y will not be exact same values. This is due to the netural GPS inaccuracy.
				# A small difference is tolerated.
                # x.accuracy and y.accuracy will be probably different.
                # But distance between x and y should be less than (x.accuracy + y.accuracy).               
                assert calc_distance(float(noaddon.geolocation.latitude),
                                    float(noaddon.geolocation.longitude),
                                    float(addonRun.geolocation.latitude),
                                    float(addonRun.geolocation.longitude)) < (float(noaddon.geolocation.accuracy) + float(addonRun.geolocation.accuracy))
            else:
                # Should be rounded real value in accuracy.
                assert is_in_accuracy(addonRun.geolocation.accuracy, expected.geolocation.accuracy['accuracy'])
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.accuracy == expected.geolocation.accuracy['value']


## Test position's altitude in meters, relative to sea level.
def test_altitude(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.altitude is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.altitude['value'] == 'REAL VALUE':
        if addonRun.geolocation.altitude == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.altitude == noaddon.geolocation.altitude
        else:
            if expected.geolocation.altitude['accuracy'] == 'EXACTLY':
                # Values do not have to be strictly equal.
                # A deviation of less than 10 meters is tolerated.
                assert abs(float(addonRun.geolocation.altitude) - float(noaddon.geolocation.altitude)) < 10
            else:
                # Should be rounded real value in accuracy.
                assert is_in_accuracy(addonRun.geolocation.altitude, expected.geolocation.altitude['accuracy'])
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.altitude == expected.geolocation.altitude['value']


## Test accuracy of the altitude property in meters.
def test_altitudeaccurac(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.altitudeAccurac is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.altitudeAccurac['value'] == 'REAL VALUE':
        if addonRun.geolocation.altitudeAccurac == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.altitudeAccurac == noaddon.geolocation.altitudeAccurac
        else:
            if expected.geolocation.altitudeAccurac['accuracy'] == 'EXACTLY':
                # Values do not have to be strictly equal.
                # A deviation of less than 10 meters is tolerated.
                assert abs(float(addonRun.geolocation.altitudeAccurac) - float(noaddon.geolocation.altitudeAccurac)) < 10
            else:
                # Should be rounded real value in accuracy.
                assert is_in_accuracy(addonRun.geolocation.altitudeAccurac,
                                      expected.geolocation.altitudeAccurac['accuracy'])
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.altitudeAccurac == expected.geolocation.altitudeAccurac['value']


## Test heading.
#
# Heading is the direction in which the device is traveling. This value, specified in degrees,
# indicates how far off from heading true north the device is. 0 degrees represents true north,
# and the direction is determined clockwise (east is 90 degrees and west is 270 degrees).
# If speed is 0, heading is NaN. If the device is unable to provide heading information, this value is null
def test_heading(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.heading is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.heading['value'] == 'REAL VALUE':
        if addonRun.geolocation.heading == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.heading == noaddon.geolocation.heading
        else:
            if expected.geolocation.heading['accuracy'] == 'EXACTLY':
                # Values do not have to be strictly equal.
                # A deviation of less than 30 degrees is tolerated.
                assert abs(float(addonRun.geolocation.heading) - float(noaddon.geolocation.heading)) < 30
            else:
                # Should be rounded real value in accuracy.
                assert is_in_accuracy(addonRun.geolocation.heading, expected.geolocation.heading['accuracy'])
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.heading == expected.geolocation.heading['value']


## Test position's latitude in decimal degrees.
def test_latitude(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.latitude is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.latitude['value'] == 'REAL VALUE':
        if addonRun.geolocation.latitude == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.latitude == noaddon.geolocation.latitude
        else:
            if expected.geolocation.latitude['accuracy'] == 'EXACTLY':
                # Values do not have to be strictly equal.
                # A deviation of less than 1 degrees is tolerated.
                assert abs(float(addonRun.geolocation.latitude) - float(noaddon.geolocation.latitude)) < 1
            else:
                real_latitude = float(noaddon.geolocation.latitude)
                spoofed_latitude = float(addonRun.geolocation.latitude)
                max_allowed_deviation = expected.geolocation.latitude['accuracy']
                assert abs(real_latitude - spoofed_latitude) < max_allowed_deviation
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.latitude == expected.geolocation.latitude['value']


## Test position's longitude in decimal degrees.
def test_longitude(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.longitude is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.longitude['value'] == 'REAL VALUE':
        if addonRun.geolocation.longitude == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.longitude == noaddon.geolocation.longitude
        else:
            if expected.geolocation.longitude['accuracy'] == 'EXACTLY':
                # Values do not have to be strictly equal.
                # A deviation of less than 1 degrees is tolerated.
                assert abs(float(addonRun.geolocation.longitude) - float(noaddon.geolocation.longitude)) < 1
            else:
                real_longitude = float(noaddon.geolocation.longitude)
                spoofed_longitude = float(addonRun.geolocation.longitude)
                max_allowed_deviation = expected.geolocation.longitude['accuracy']
                assert abs(real_longitude - spoofed_longitude) < max_allowed_deviation
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.longitude == expected.geolocation.longitude['value']


## Test speed (velocity) of the device in meters per second. This value can be null.
def test_speed(noaddon, addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.speed is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.speed['value'] == 'REAL VALUE':
        if addonRun.geolocation.speed == "null":
            # If current value is null, real value has to be null too.
            assert addonRun.geolocation.speed == noaddon.geolocation.speed
        else:
            if expected.geolocation.speed['accuracy'] == 'EXACTLY':
                # Values do not have to be strictly equal.
                # A deviation of less than 5 meters per second is tolerated.
                assert abs(float(addonRun.geolocation.speed) - float(noaddon.geolocation.speed)) < 5
            else:
                # Should be rounded real value in accuracy.
                assert is_in_accuracy(addonRun.geolocation.speed, expected.geolocation.speed['accuracy'])
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.speed == expected.geolocation.speed['value']


## Test timestamp.
def test_timestamp(addonRun, expected):
    if get_shared_addonRun().geolocation.valid == False:
        pytest.xfail("Geolocation not supported during this run.")
    if get_shared_addonRun().geolocation.timestamp is None:
        pytest.skip("Geolocation not tested.")
    if expected.geolocation.timestamp['value'] == 'REAL VALUE':
        if expected.geolocation.timestamp['accuracy'] == 'EXACTLY':
            # Values do not have to be strictly equal because executing command takes some time.
            # A deviation of less than 2 seconds is tolerated.
            #assert abs(time() - int(addonRun.geolocation.timestamp)/1000) < 2
            pass
        else:
            timestamp_accuracy = expected.geolocation.timestamp['accuracy']*1000
            # Should be rounded real value in accuracy.
            assert is_in_accuracy(addonRun.geolocation.timestamp, timestamp_accuracy)
    else:
        # Should be spoofed value.
        assert addonRun.geolocation.timestamp == expected.geolocation.timestamp['value']
