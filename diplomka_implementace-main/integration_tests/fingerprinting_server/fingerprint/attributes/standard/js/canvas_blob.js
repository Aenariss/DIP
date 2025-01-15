/*
#  JShelter is a browser extension which increases level
#  of security, anonymity and privacy of the user while browsing the
#  internet.
#
#  Copyright (C) 2022  Martin Bednar
#  Copyright (C) 2024  Jana Petranova
#  Copyright (C) 2021  Matus Svancar
#
#  SPDX-License-Identifier: GPL-3.0-or-later
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
*/ 

function get_blob_canvas(name) {
    try {
        var canvas = document.getElementById(name);
        return new Promise(function(resolve, reject) {
            canvas.toBlob(function(blob) {
                if (blob) {
                    resolve(blob.arrayBuffer().then(a => Array.from(new Int8Array(a))));
                } else {
                    resolve("Blob is null or undefined");
                }
            });
        });
    } catch (error) {
        return "ERROR";
    }
}

(function() {
    api.register("canvas_blob", async function () {
        try {
            var canvas_blob = {
                'name': 'canvas_blob',
                'data': '0'};

            canvas_blob.data = await get_blob_canvas('canvasx');
        } catch(e){
            canvas_blob.data = "Not supported " + e;
        }
        return canvas_blob;
    });
})();
