(function() {
    api.register("WebGL", function () {
        var startTime = performance.now();
        var device = {
            'webglVendor': null,
            'webglRenderer': null,
            'maxVertexUniformComponents': 0,
            'maxVertexUniformBlocks': 0,
            'maxVertexOutputComponents': 0,
            'maxVaryingComponents': 0,
            'maxTransformFeedbackInterleavedComponents': 0,
            'maxFragmentUniformComponents': 0,
            'maxFragmentUniformBlocks' : 0,
            'maxFragmentInputComponents': 0,
            'maxUniformBufferBindings': 0,
            'maxCombinedUniformBlocks': 0,
            'maxCombinedVertexUniformComponents': 0,
            'maxCombinedFragmentUniformComponents': 0,
            'maxVertexAttribs': 0,
            'maxVertexUniformVectors': 0,
            'maxVertexTextureImageUnits': 0,
            'maxTextureSize': 0,
            'maxCubeMapTextureSize': 0,
            'max3DTextureSize': 0,
            'maxArrayTextureLayers': 0,
            'webGLpixels': 0,
            'webGLdataURL': 0,
            'webGLpercisions': [],
            'timeTaken': null
        };
        try {
            var canvas = document.getElementById('webglCanvas');

            var gl = canvas.getContext("webgl2", { preserveDrawingBuffer: true}) ||
                canvas.getContext("experimental-webgl2", { preserveDrawingBuffer: true}) ||
                canvas.getContext("webgl", { preserveDrawingBuffer: true}) ||
                canvas.getContext("experimental-webgl", { preserveDrawingBuffer: true}) ||
                canvas.getContext("moz-webgl", { preserveDrawingBuffer: true});


        try {
                var buff = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, buff);
                var n = new Float32Array([-.2, -.9, 0, .4, -.26, 0, 0, .7321, 0]);
                gl.bufferData(gl.ARRAY_BUFFER, n, gl.STATIC_DRAW), buff.itemSize = 3, buff.numItems = 3;
                var prog = gl.createProgram();
                var o = gl.createShader(gl.VERTEX_SHADER);
                gl.shaderSource(o, "attribute vec2 attrVertex;varying vec2 varyinTexCoordinate;uniform vec2 uniformOffset;void main(){varyinTexCoordinate=attrVertex+uniformOffset;gl_Position=vec4(attrVertex,0,1);}");
                gl.compileShader(o);
                var n = gl.createShader(gl.FRAGMENT_SHADER);
                gl.shaderSource(n, "precision mediump float;varying vec2 varyinTexCoordinate;void main() {gl_FragColor=vec4(varyinTexCoordinate,0,1);}"),
                gl.compileShader(n);
                gl.attachShader(prog, o);
                gl.attachShader(prog, n);
                gl.linkProgram(prog);
                gl.useProgram(prog);
                prog.vertexPosAttrib = gl.getAttribLocation(prog, "attrVertex");
                prog.offsetUniform = gl.getUniformLocation(prog, "uniformOffset");
                gl.enableVertexAttribArray(prog.vertexPosArray);
                gl.vertexAttribPointer(prog.vertexPosAttrib, buff.itemSize, gl.FLOAT, !1, 0, 0);
                gl.uniform2f(prog.offsetUniform, 1, 1);
                gl.drawArrays(gl.TRIANGLE_STRIP, 0, buff.numItems);
            } catch (e) {
                console.log(e);
            }

            device.webGLdataURL = gl.canvas.toDataURL();

            if (gl) {
                device.webglVendor = gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_VENDOR_WEBGL);
                device.webglRenderer = gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL);
                device.maxVertexUniformComponents = gl.getParameter(gl.MAX_VERTEX_UNIFORM_COMPONENTS);
                device.maxVertexUniformBlocks = gl.getParameter(gl.MAX_VERTEX_UNIFORM_BLOCKS);
                device.maxVertexOutputComponents = gl.getParameter(gl.MAX_VERTEX_OUTPUT_COMPONENTS);
                device.maxVaryingComponents = gl.getParameter(gl.MAX_VARYING_COMPONENTS);
                device.maxTransformFeedbackInterleavedComponents = gl.getParameter(gl.MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS);
                device.maxFragmentUniformComponents = gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_COMPONENTS);
                device.maxFragmentUniformBlocks = gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_BLOCKS);
                device.maxFragmentInputComponents = gl.getParameter(gl.MAX_FRAGMENT_INPUT_COMPONENTS);
                device.maxUniformBufferBindings = gl.getParameter(gl.MAX_UNIFORM_BUFFER_BINDINGS);
                device.maxCombinedUniformBlocks = gl.getParameter(gl.MAX_COMBINED_UNIFORM_BLOCKS);
                device.maxCombinedVertexUniformComponents = gl.getParameter(gl.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS);
                device.maxCombinedFragmentUniformComponents = gl.getParameter(gl.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS);
                device.maxVertexAttribs = gl.getParameter(gl.MAX_VERTEX_ATTRIBS);
                device.maxVertexUniformVectors = gl.getParameter(gl.MAX_VERTEX_UNIFORM_VECTORS);
                device.maxVertexTextureImageUnits = gl.getParameter(gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS);
                device.maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
                device.maxCubeMapTextureSize = gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE);
                device.max3DTextureSize = gl.getParameter(gl.MAX_3D_TEXTURE_SIZE);
                device.maxArrayTextureLayers = gl.getParameter(gl.MAX_ARRAY_TEXTURE_LAYERS);
            }

            var glPixels = canvas.getContext('webgl2', {preserveDrawingBuffer: true}) ||
                     canvas.getContext('experimental-webgl2', {preserveDrawingBuffer: true}) ||
                     canvas.getContext('webgl', {preserveDrawingBuffer: true}) ||
                     canvas.getContext('experimental-webgl', {preserveDrawingBuffer: true}) ||
                     canvas.getContext('moz-webgl', {preserveDrawingBuffer: true});
              
            var imageData = new Uint8Array(glPixels.canvas.width*glPixels.canvas.height*4);

            glPixels.readPixels(0, 0, glPixels.canvas.width, glPixels.canvas.height, glPixels.RGBA, glPixels.UNSIGNED_BYTE, imageData);   

            device.webGLpixels = imageData;      

            var canvasperc = document.getElementById('webglCanvas');
            
            var glperc = canvasperc.getContext('webgl2') || 
                         canvasperc.getContext('experimental-webgl2') || 
                         canvasperc.getContext('webgl') || 
                         canvasperc.getContext('experimental-webgl') || 
                         canvasperc.getContext('moz-webgl');
                         

            try {
                var arr = [];
                var shaderTypes = ['FRAGMENT_SHADER', 'VERTEX_SHADER'];
                var precisionTypes = ['LOW_FLOAT', 'MEDIUM_FLOAT', 'HIGH_FLOAT', 'LOW_INT', 'MEDIUM_INT', 'HIGH_INT'];
                for (var i = 0; i < shaderTypes.length; i++) {
                    for (var j = 0; j < precisionTypes.length; j++) {
                        var precisionFormat = glperc.getShaderPrecisionFormat(glperc[shaderTypes[i]], glperc[precisionTypes[j]]);
                        arr.push({
                            shaderType: shaderTypes[i],
                            precisionType: precisionTypes[j],
                            rangeMin: precisionFormat.rangeMin,
                            rangeMax: precisionFormat.rangeMax,
                            precision: precisionFormat.precision
                        });
                    }
                }
                device.webGLpercisions = arr
                var endTime = performance.now();
                device.timeTaken = endTime - startTime;
            } catch (e) {
                device.webGLpercisions = []
            }

            return device;
        } catch (e) {
            var endTime = performance.now();
            device.timeTaken = endTime - startTime;
            console.log("error occured at webgl");
            return device;
        }
    });
})();
