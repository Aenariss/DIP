(function() {
    api.register("openDB", function () {
        try {
            return !!window.openDatabase ? "yes" : "no";
        } catch(e){ 
            return "js blocked";
        }
    });
})();
