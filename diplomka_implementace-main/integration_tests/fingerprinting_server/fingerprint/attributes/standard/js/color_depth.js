(function() {
    api.register("color depth", function () {
        try {
            return window.screen.colorDepth;
        }
        catch(e) {
            return "js blocked";
        }
        
    });
})();
