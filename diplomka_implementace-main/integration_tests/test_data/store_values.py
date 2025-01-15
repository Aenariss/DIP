#
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


import json
import os
from values_tested import TestedValues

'''
Read an output JSON file. If you are interested in testing for more attributes, you can get them
out of the file in this function.
'''
def read_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        navigator = data.get('navigator', {})
        geolocation = data.get('geolocation', {})
        device = data.get('device', {})
        audio = data.get('audio', {})
        canvas = data.get('canvas', {})
        webgl = data.get('WebGL', {})


        test_case = TestedValues(data.get('_pet'),
                                 navigator.get('userAgent'),
                                 navigator.get('appVersion'),
                                 navigator.get('platform'),
                                 navigator.get('vendor'),
                                 navigator.get('language'),
                                 navigator.get('languages'),
                                 navigator.get('doNotTrack'),
                                 navigator.get('cookieEnabled'),
                                 navigator.get('oscpu'),
                                 navigator.get('plugins'),
                                 navigator.get('mimeTypes'),

                                 geolocation.get('accuracy'),
                                 geolocation.get('altitude'),
                                 geolocation.get('altitudeAccuracy'),
                                 geolocation.get('heading'),
                                 geolocation.get('latitude'),
                                 geolocation.get('longitude'),
                                 geolocation.get('speed'),
                                 geolocation.get('timestamp'),
                                 geolocation.get('valid'),

                                 device.get('deviceMemory'),
                                 device.get('hardwareConcurrency'),
                                 data.get('io_devices'),

                                 audio.get('channelDataResult'),
                                 audio.get('channelDataResult2'),
                                 audio.get('copyResult'),
                                 audio.get('copyResult2'),
                                 
                                 audio.get('byteFrequencyResult'),
                                 audio.get('floatFrequencyResult'),                                 
                                 audio.get('byteTimeResult'),
                                 audio.get('floatTimeResult'),

                                 data.get('time'),
                                 data.get('performance'),
                                 canvas.get('spoof'),

                                 canvas.get('imageData'),
                                 canvas.get('dataURL'),
                                 data.get('canvas_blob'),
                                 canvas.get('pointInPath'),
                                 canvas.get('pointInStroke'),

                                 data.get('WebGL'),
                                 webgl.get('webGLpercisions'), 
                                 webgl.get('webGLpixels'),
                                 webgl.get('webGLdataURL'),

                                 data.get('worker'),
                                 
                                 data.get('methodsToString'),
                                 data.get('ECMAarrays')
                                 )
        return test_case
    except FileNotFoundError:
        print("File not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format.")
    except Exception as e:
        print("An error occurred:", e)

'''
Gather data from server output files and mark them based on extensions used.
'''
def create_browser_data(subfolder):

    results = os.path.join('/usr/app/src/fingerprinting_server/outputs', subfolder)
    testing_data = []

    for filename in os.listdir(results):
        if "None" in filename:
            testing_data.insert(0, read_data(results + "/" + filename))
        else: 
            testing_data.append(read_data(results + "/" + filename))

    return testing_data
