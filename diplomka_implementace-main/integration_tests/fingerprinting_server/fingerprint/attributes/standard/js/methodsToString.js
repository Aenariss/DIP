var APIs = {
    "Date": {
        "static_methods": [
            "now",
            "parse",
            "UTC"
        ],
        "instance_methods": [
            "getDate",
            "getDay",
            "getFullYear",
            "getHours",
            "getMilliseconds",
            "getMinutes",
            "getMonth",
            "getSeconds",
            "getTime",
            "getTimezoneOffset",
            "getUTCDate",
            "getUTCDay",
            "getUTCFullYear",
            "getUTCHours",
            "getUTCMilliseconds",
            "getUTCMinutes",
            "getUTCMonth",
            "getUTCSeconds",
            "getYear",
            "setDate",
            "setFullYear",
            "setHours",
            "setMilliseconds",
            "setMinutes",
            "setMonth",
            "setSeconds",
            "setTime",
            "setUTCDate",
            "setUTCFullYear",
            "setUTCHours",
            "setUTCMilliseconds",
            "setUTCMinutes",
            "setUTCMonth",
            "setUTCSeconds",
            "setYear",
            "toDateString",
            "toISOString",
            "toJSON",
            "toGMTString",
            "toLocaleDateString",
            "toLocaleString",
            "toString",
            "toTimeString",
            "toUTCString",
            "valueOf"
        ]
    },
    "performance": {
        "static_methods": [
            "now",
            "clearMarks",
            "clearMeasures",
            "clearResourceTimings",
            "getEntries",
            "getEntriesByName",
            "getEntriesByType",
            "mark",
            "measure",
            "setResourceTimingBufferSize",
            "toJSON"
        ]
    },
    "navigator": {
        "static_methods": [
            "getCurrentPosition",
            "watchPosition",
            "clearWatch"
        ]
    },
    "canvas": {
        "inject_code": "var canvas = document.getElementById('canvas1');",
        "static_methods": [
            "getContext"
        ]
    }
}



function getAPIStrings () {
    var result = {};
    for (let API in APIs) { 
        if ('static_methods' in APIs[API]) { 
            var inject_code = "";

            if ('inject_code' in APIs[API]) {
                inject_code = APIs[API]['inject_code'];
            }

            for (let method of APIs[API]['static_methods']) { 
                let method_toString = "";
                
                try { 
                    method_toString = eval("(function() {" + inject_code + "return " + API + "." + method + ".toString();})()");
                    result[API + '.' + method] = method_toString
                } catch (error) { 
                    result[API + '.' + method] = null
                }
            }
        }
        if ('instance_methods' in APIs[API]) { 
            var constructor_toString = ""

            try {
                constructor_toString = eval("(function() {" + "return " + API + ".toString();})()");
                result[API] = constructor_toString;

            } catch (error) {
                result[API] = null;
            }
            for (let method of APIs[API]['instance_methods']) {
                var method_toString = ""

                try {
                    method_toString = eval("(function() {" + "return " + API + "." + method + ".toString();})()");
                    result[API + '.prototype.' + method] = method_toString;

                } catch (error) {
                    result[API + '.prototype.' + method] = null;
                }

                method_toString = ""

                try {
                    method_toString = eval("(function() {" + "return new " + API + "()." + method + ".toString();})()");
                    result[API + '.' + method] = method_toString;
                } catch (error) {
                    result[API + '.' + method] = null;
                }
             }
         }
    }
    return result;
};

(function() {
    api.register("methodsToString", function () {
        try {
            var toString = getAPIStrings();
            return toString;
        }
        catch(e) {
            return "js blocked";
        }
    });
})();