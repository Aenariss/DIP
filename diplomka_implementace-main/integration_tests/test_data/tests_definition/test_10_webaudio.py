#
#  Copyright (C) 2021  Matus Svancar
#  Copyright (C) 2022  Libor Polčák
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
import numpy as np
from shared_set import get_shared_level, get_shared_addonRun


def assertNotEqualNumbersInTexts(spoofed, orig, max_similarity = 0.05):
    """
    max_similarity: As data are changed probabilistically, we can tolerate some data that are the
    same.
    """
    assert len(spoofed) == len(orig)
    not_changed = 0
    spoofed_np = np.asarray(spoofed, dtype=np.float64)
    orig_np = np.asarray(orig, dtype=np.float64)
    for x, y in zip(spoofed_np, orig_np):
        if x == y:
            not_changed += 1
    assert not_changed < (max_similarity * len(orig))

## Test AudioContext.getChannelData
def test_channel_data(noaddon, addonRun, expected):
    if get_shared_addonRun().audio.get_channel is None:
        pytest.skip("Audio not tested.")
    if addonRun.audio:
        if expected.audio.get_channel == 'SPOOF VALUE':
            assert addonRun.audio.get_channel != noaddon.audio.get_channel
            assertNotEqualNumbersInTexts(addonRun.audio.get_channel, noaddon.audio.get_channel)
        else:
            assert addonRun.audio.get_channel == noaddon.audio.get_channel
    else:
        assert False

## Test that repeated calls of getChannelData (interleaved with copyFromChannel) return the same data
def test_multiple_get_channel_data(addonRun):
    if get_shared_addonRun().audio.get_channel is None:
        pytest.skip("Audio not tested.")
    assert addonRun.audio.get_channel == addonRun.audio.get_channel2

## Test AudioContext.copyFromChannel
def test_copy_channel(noaddon, addonRun, expected):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    if addonRun.audio:
        if expected.audio.copy_channel == 'SPOOF VALUE':
            assert addonRun.audio.copy_channel != noaddon.audio.copy_channel
            assertNotEqualNumbersInTexts(addonRun.audio.copy_channel, noaddon.audio.copy_channel)
        else:
            assert addonRun.audio.copy_channel == noaddon.audio.copy_channel
    else:
        assert False

## Test that repeated calls of copyFromChannel (interleaved with getChannelData) return the same data
def test_multiple_copy_channel(addonRun):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    if get_shared_level() == 3:
        # Note that it is not possible to use xfail as decorator as those are evaluated during
        # module import and the module is not reimported for different levels
        pytest.xfail("JShelter creates different white noise during each copyFromChannel() call. As we do not care about fingerprintability in this level, we do not care that the noise is different")
    assert addonRun.audio.copy_channel == addonRun.audio.copy_channel2

## Test that getChannelData and copyFromChannel return the same data
def test_get_channel_equal_copy_channel(addonRun):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    if get_shared_level() == 3:
        # Note that it is not possible to use xfail as decorator as those are evaluated during
        # module import and the module is not reimported for different levels
        pytest.xfail("JShelter creates different white noise during each copyFromChannel() call. As we do not care about fingerprintability in this level, we do not care that the noise is different")
    assert addonRun.audio.copy_channel == addonRun.audio.get_channel

## Test AnalyserNode.getByteTimeDomainData
def test_byte_time_domain(noaddon, addonRun, expected):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    #js_level = get_shared_level()
    #if js_level == 3:
        # Note that it is not possible to use xfail as decorator as those are evaluated during
        # module import and the module is not reimported for different levels
    #    pytest.xfail("This test will work only after Array Wrappers are fixed in Firefox")

    if addonRun.audio:
        if expected.audio.byte_time_domain == 'SPOOF VALUE':
            assert addonRun.audio.byte_time_domain != noaddon.audio.byte_time_domain
            assertNotEqualNumbersInTexts(addonRun.audio.byte_time_domain,
                                         noaddon.audio.byte_time_domain,
                                         0.7) # The code modifies the value with 0.5 probability
        else:
            assert addonRun.audio.byte_time_domain == noaddon.audio.byte_time_domain
    else:
        assert False

## Test AnalyserNode.getFloatTimeDomainData
def test_float_time_domain(noaddon, addonRun, expected):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    #js_level = get_shared_level()
    #if js_level == 3:
        # Note that it is not possible to use xfail as decorator as those are evaluated during
        # module import and the module is not reimported for different levels
    #    pytest.xfail("This test will work only after Array Wrappers are fixed in Firefox")
    if addonRun.audio:
        if expected.audio.float_time_domain == 'SPOOF VALUE':
            assert addonRun.audio.float_time_domain != noaddon.audio.float_time_domain
            assertNotEqualNumbersInTexts(addonRun.audio.float_time_domain, noaddon.audio.float_time_domain)
        else:
            assert addonRun.audio.float_time_domain == noaddon.audio.float_time_domain
    else:
        assert False

## Test AnalyserNode.getByteFrequencyData
def test_byte_frequency(noaddon, addonRun, expected):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    if addonRun.audio:
        if expected.audio.byte_frequency == 'SPOOF VALUE':
            assert addonRun.audio.byte_frequency != noaddon.audio.byte_frequency
            assertNotEqualNumbersInTexts(addonRun.audio.byte_frequency,
                                         noaddon.audio.byte_frequency,
                                         0.7) # The code modifies the value with 0.5 probability
        else:
            assert addonRun.audio.byte_frequency == noaddon.audio.byte_frequency
    else:
        assert False

## Test AnalyserNode.getFloatFrequencyData
def test_float_frequency(noaddon, addonRun, expected):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    if addonRun.audio:
        if expected.audio.float_frequency == 'SPOOF VALUE':
            assert addonRun.audio.float_frequency != noaddon.audio.float_frequency
            assertNotEqualNumbersInTexts(addonRun.audio.float_frequency, noaddon.audio.float_frequency)
        else:
            assert addonRun.audio.float_frequency == noaddon.audio.float_frequency
    else:
        assert False

## Test little lies farbling
def test_little_lies(noaddon, addonRun):
    if get_shared_addonRun().audio.copy_channel is None:
        pytest.skip("Audio not tested.")
    if get_shared_level() != 2:
        pytest.skip("Apply the test to the little lies level only")
    def assertNumberesSimilar(spoofed, orig, epsilon):
        assert len(spoofed) == len(orig)
        spoofed_np = np.asarray(spoofed, dtype=np.float64)
        orig_np = np.asarray(orig, dtype=np.float64)
        for x, y in zip(spoofed_np, orig_np):
            assert abs(x - y) <= epsilon
    assertNumberesSimilar(addonRun.audio.get_channel, noaddon.audio.get_channel, 0.01)
    assertNumberesSimilar(addonRun.audio.copy_channel, noaddon.audio.copy_channel, 0.01)
    # See issue 114 for more details why the following lines are commented out
    #assertNumberesSimilar(audio_data['byte_time_domain'], browser.real.audio.byte_time_domain, 1)
    #assertNumberesSimilar(audio_data['float_time_domain'], browser.real.audio.float_time_domain, 0.01)
    #assertNumberesSimilar(audio_data['byte_frequency'], browser.real.audio.byte_frequency, 1)
    #assertNumberesSimilar(audio_data['float_frequency'], browser.real.audio.float_frequency, 0.01)
