#
#  Copyright (C) 2021  Matus Svancar
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

import pytest
from shared_set import get_shared_addonRun

# Test WebGLRenderingContext.getParameter for unmaskedVendor
def test_unmasked_vendor(noaddon, addonRun, expected):
    if get_shared_addonRun().webglParameters is None:
        pytest.skip("WebGL not tested.")
    if expected.webglParameters == 'REAL VALUE':
        assert addonRun.webglParameters['webglVendor'] == noaddon.webglParameters['webglVendor']
    else:
        if addonRun.webglParameters['webglVendor'] == noaddon.webglParameters['webglVendor']:
            assert addonRun.webglParameters['webglVendor'] == ""
        else:
            assert True

# Test WebGLRenderingContext.getParameter for unmaskedRenderer
def test_unmasked_renderer(noaddon, addonRun, expected):
    if get_shared_addonRun().webglParameters is None:
        pytest.skip("WebGL not tested.")
    if expected.webglParameters == 'REAL VALUE':
        assert addonRun.webglParameters['webglRenderer'] == noaddon.webglParameters['webglRenderer']
    else:
        assert addonRun.webglParameters['webglRenderer'] != noaddon.webglParameters['webglRenderer']

# Test WebGLRenderingContext.getParameter
def test_other_parameters(noaddon, addonRun, expected):
    if get_shared_addonRun().webglParameters is None:
        pytest.skip("WebGL not tested.")
    if expected.webglParameters == 'SPOOF VALUE':
        spoof_sum = 0
        if noaddon.webglParameters['maxVertexUniformComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxVertexUniformComponents'] <= noaddon.webglParameters['maxVertexUniformComponents']
            spoof_sum += noaddon.webglParameters['maxVertexUniformComponents'] - addonRun.webglParameters['maxVertexUniformComponents']
        if noaddon.webglParameters['maxVertexUniformBlocks'] != None:
            assert 0 <= addonRun.webglParameters['maxVertexUniformBlocks'] <= noaddon.webglParameters['maxVertexUniformBlocks']
            spoof_sum += noaddon.webglParameters['maxVertexUniformBlocks'] - addonRun.webglParameters['maxVertexUniformBlocks']
        if noaddon.webglParameters['maxVertexOutputComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxVertexOutputComponents'] <= noaddon.webglParameters['maxVertexOutputComponents']
            spoof_sum += noaddon.webglParameters['maxVertexOutputComponents'] - addonRun.webglParameters['maxVertexOutputComponents']
        if noaddon.webglParameters['maxVaryingComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxVaryingComponents'] <= noaddon.webglParameters['maxVaryingComponents']
            spoof_sum += noaddon.webglParameters['maxVaryingComponents'] - addonRun.webglParameters['maxVaryingComponents']
        if noaddon.webglParameters['maxTransformFeedbackInterleavedComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxTransformFeedbackInterleavedComponents'] <= noaddon.webglParameters['maxTransformFeedbackInterleavedComponents']
            spoof_sum += noaddon.webglParameters['maxTransformFeedbackInterleavedComponents'] - addonRun.webglParameters['maxTransformFeedbackInterleavedComponents']
        if noaddon.webglParameters['maxFragmentUniformComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxFragmentUniformComponents'] <= noaddon.webglParameters['maxFragmentUniformComponents']
            spoof_sum += noaddon.webglParameters['maxFragmentUniformComponents'] - addonRun.webglParameters['maxFragmentUniformComponents']
        if noaddon.webglParameters['maxFragmentUniformBlocks'] != None:
            assert 0 <= addonRun.webglParameters['maxFragmentUniformBlocks'] <= noaddon.webglParameters['maxFragmentUniformBlocks']
            spoof_sum += noaddon.webglParameters['maxFragmentUniformBlocks'] - addonRun.webglParameters['maxFragmentUniformBlocks']
        if noaddon.webglParameters['maxFragmentInputComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxFragmentInputComponents'] <= noaddon.webglParameters['maxFragmentInputComponents']
            spoof_sum += noaddon.webglParameters['maxFragmentInputComponents'] - addonRun.webglParameters['maxFragmentInputComponents']
        if noaddon.webglParameters['maxUniformBufferBindings'] != None:
            assert 0 <= addonRun.webglParameters['maxUniformBufferBindings'] <= noaddon.webglParameters['maxUniformBufferBindings']
            spoof_sum += noaddon.webglParameters['maxUniformBufferBindings'] - addonRun.webglParameters['maxUniformBufferBindings']
        if noaddon.webglParameters['maxCombinedUniformBlocks'] != None:
            assert 0 <= addonRun.webglParameters['maxCombinedUniformBlocks'] <= noaddon.webglParameters['maxCombinedUniformBlocks']
            spoof_sum += noaddon.webglParameters['maxCombinedUniformBlocks'] - addonRun.webglParameters['maxCombinedUniformBlocks']
        if noaddon.webglParameters['maxCombinedVertexUniformComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxCombinedVertexUniformComponents'] <= noaddon.webglParameters['maxCombinedVertexUniformComponents']
            spoof_sum += noaddon.webglParameters['maxCombinedVertexUniformComponents'] - addonRun.webglParameters['maxCombinedVertexUniformComponents']
        if noaddon.webglParameters['maxCombinedFragmentUniformComponents'] != None:
            assert 0 <= addonRun.webglParameters['maxCombinedFragmentUniformComponents'] <= noaddon.webglParameters['maxCombinedFragmentUniformComponents']
            spoof_sum += noaddon.webglParameters['maxCombinedFragmentUniformComponents'] - addonRun.webglParameters['maxCombinedFragmentUniformComponents']
        if noaddon.webglParameters['maxVertexAttribs'] != None:
            assert 0 <= addonRun.webglParameters['maxVertexAttribs'] <= noaddon.webglParameters['maxVertexAttribs']
            spoof_sum += noaddon.webglParameters['maxVertexAttribs'] - addonRun.webglParameters['maxVertexAttribs']
        if noaddon.webglParameters['maxVertexUniformVectors'] != None:
            assert 0 <= addonRun.webglParameters['maxVertexUniformVectors'] <= noaddon.webglParameters['maxVertexUniformVectors']
            spoof_sum += noaddon.webglParameters['maxVertexUniformVectors'] - addonRun.webglParameters['maxVertexUniformVectors']
        if noaddon.webglParameters['maxVertexTextureImageUnits'] != None:
            assert 0 <= addonRun.webglParameters['maxVertexTextureImageUnits'] <= noaddon.webglParameters['maxVertexTextureImageUnits']
            spoof_sum += noaddon.webglParameters['maxVertexTextureImageUnits'] - addonRun.webglParameters['maxVertexTextureImageUnits']
        if noaddon.webglParameters['maxTextureSize'] != None:
            assert 0 <= addonRun.webglParameters['maxTextureSize'] <= noaddon.webglParameters['maxTextureSize']
            spoof_sum += noaddon.webglParameters['maxTextureSize'] - addonRun.webglParameters['maxTextureSize']
        if noaddon.webglParameters['maxCubeMapTextureSize'] != None:
            assert 0 <= addonRun.webglParameters['maxCubeMapTextureSize'] <= noaddon.webglParameters['maxCubeMapTextureSize']
            spoof_sum += noaddon.webglParameters['maxCubeMapTextureSize'] - addonRun.webglParameters['maxCubeMapTextureSize']
        if noaddon.webglParameters['max3DTextureSize'] != None:
            assert 0 <= addonRun.webglParameters['max3DTextureSize'] <= noaddon.webglParameters['max3DTextureSize']
            spoof_sum += noaddon.webglParameters['max3DTextureSize'] - addonRun.webglParameters['max3DTextureSize']
        if noaddon.webglParameters['maxArrayTextureLayers'] != None:
            assert 0 <= addonRun.webglParameters['maxArrayTextureLayers'] <= noaddon.webglParameters['maxArrayTextureLayers']
            spoof_sum += noaddon.webglParameters['maxArrayTextureLayers'] - addonRun.webglParameters['maxArrayTextureLayers']
        assert spoof_sum > 0
    elif expected.webglParameters == 'ZERO VALUE':
        assert (addonRun.webglParameters['maxVertexUniformComponents'] == 0)
        assert (addonRun.webglParameters['maxVertexUniformBlocks'] == 0)
        assert (addonRun.webglParameters['maxVertexOutputComponents'] == 0)
        assert (addonRun.webglParameters['maxVaryingComponents'] == 0)
        assert (addonRun.webglParameters['maxTransformFeedbackInterleavedComponents'] == 0)
        assert (addonRun.webglParameters['maxFragmentUniformComponents'] == 0)
        assert (addonRun.webglParameters['maxFragmentUniformBlocks'] == 0)
        assert (addonRun.webglParameters['maxFragmentInputComponents'] == 0)
        assert (addonRun.webglParameters['maxUniformBufferBindings'] == 0)
        assert (addonRun.webglParameters['maxCombinedUniformBlocks'] == 0)
        assert (addonRun.webglParameters['maxCombinedVertexUniformComponents'] == 0)
        assert (addonRun.webglParameters['maxCombinedFragmentUniformComponents'] == 0)
        assert (addonRun.webglParameters['maxVertexAttribs'] == 0)
        assert (addonRun.webglParameters['maxVertexUniformVectors'] == 0)
        assert (addonRun.webglParameters['maxVertexTextureImageUnits'] == 0)
        assert (addonRun.webglParameters['maxTextureSize'] == 0)
        assert (addonRun.webglParameters['maxCubeMapTextureSize'] == 0)
        assert (addonRun.webglParameters['max3DTextureSize'] == 0)
        assert (addonRun.webglParameters['maxArrayTextureLayers'] == 0)
    else:
        assert (addonRun.webglParameters['maxVertexUniformComponents'] == noaddon.webglParameters['maxVertexUniformComponents'] )
        assert (addonRun.webglParameters['maxVertexUniformBlocks'] == noaddon.webglParameters['maxVertexUniformBlocks'])
        assert (addonRun.webglParameters['maxVertexOutputComponents'] == noaddon.webglParameters['maxVertexOutputComponents'])
        assert (addonRun.webglParameters['maxVaryingComponents'] == noaddon.webglParameters['maxVaryingComponents'])
        assert (addonRun.webglParameters['maxTransformFeedbackInterleavedComponents'] == noaddon.webglParameters['maxTransformFeedbackInterleavedComponents'])
        assert (addonRun.webglParameters['maxFragmentUniformComponents'] == noaddon.webglParameters['maxFragmentUniformComponents'])
        assert (addonRun.webglParameters['maxFragmentUniformBlocks']  == noaddon.webglParameters['maxFragmentUniformBlocks'])
        assert (addonRun.webglParameters['maxFragmentInputComponents'] == noaddon.webglParameters['maxFragmentInputComponents'])
        assert (addonRun.webglParameters['maxUniformBufferBindings'] == noaddon.webglParameters['maxUniformBufferBindings'])
        assert (addonRun.webglParameters['maxCombinedUniformBlocks'] == noaddon.webglParameters['maxCombinedUniformBlocks'])
        assert (addonRun.webglParameters['maxCombinedVertexUniformComponents'] == noaddon.webglParameters['maxCombinedVertexUniformComponents'])
        assert (addonRun.webglParameters['maxCombinedFragmentUniformComponents'] == noaddon.webglParameters['maxCombinedFragmentUniformComponents'])
        assert (addonRun.webglParameters['maxVertexAttribs'] == noaddon.webglParameters['maxVertexAttribs'])
        assert (addonRun.webglParameters['maxVertexUniformVectors'] == noaddon.webglParameters['maxVertexUniformVectors'])
        assert (addonRun.webglParameters['maxVertexTextureImageUnits'] == noaddon.webglParameters['maxVertexTextureImageUnits'])
        assert (addonRun.webglParameters['maxTextureSize'] == noaddon.webglParameters['maxTextureSize'])
        assert (addonRun.webglParameters['maxCubeMapTextureSize'] == noaddon.webglParameters['maxCubeMapTextureSize'])
        assert (addonRun.webglParameters['max3DTextureSize'] == noaddon.webglParameters['max3DTextureSize'])
        assert (addonRun.webglParameters['maxArrayTextureLayers'] == noaddon.webglParameters['maxArrayTextureLayers'])

# Test WebGLRenderingContext.getShaderPrecisionFormat
def test_webgl_precisions(noaddon, addonRun, expected):
    if get_shared_addonRun().webglPrecisions is None:
        pytest.skip("WebGL not tested.")
    if expected.webglPrecisions == 'ZERO VALUE':
        assert addonRun.webglPrecisions != noaddon.webglPrecisions
    else:
        assert addonRun.webglPrecisions == noaddon.webglPrecisions

# Test WebGLRenderingContext.readPixels
def test_webgl_read_pixels(noaddon, addonRun, expected):
    if get_shared_addonRun().webglPixels is None:
        pytest.skip("WebGL not tested.")
    if addonRun.webglPixels == "ERROR":
        print("\nWebGLRenderingContext.readPixels failed.")
        assert False
    if expected.webglPixels == 'SPOOF VALUE':
        assert addonRun.webglPixels != noaddon.webglPixels
    else:
        assert addonRun.webglPixels == noaddon.webglPixels

# Test HTMLCanvasElement.toDataURL on webgl canvas
def test_webgl_to_data_URL(noaddon, addonRun, expected):
    if get_shared_addonRun().webglDataURL is None:
        pytest.skip("WebGL not tested.")
    if expected.webglDataURL == 'SPOOF VALUE':
        assert addonRun.webglDataURL != noaddon.webglDataURL
    else:
        assert addonRun.webglDataURL == noaddon.webglDataURL
