(function() {
    api.register("device", function () {
        try {
            var device = {
                'deviceMemory': window.navigator.deviceMemory,
                'hardwareConcurrency': window.navigator.hardwareConcurrency
            };
            
            return device;
        } catch (e) {
            return "error" + e;
        }
    });
})();
