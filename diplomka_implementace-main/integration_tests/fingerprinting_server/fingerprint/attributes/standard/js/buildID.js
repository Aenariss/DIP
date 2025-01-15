(function() {
    api.register("buildID", function () {
        try{
            return window.navigator.buildID; }

        catch(e) {
            return "js blocker";
        }
        
    });
})();
