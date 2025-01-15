(function() {
    api.register("IE addBehavior", function () {
    try {
        if(document.body && document.body.addBehavior) {
            return "yes"; } 
        else { return "no"; }
        }
        catch(e){
            return "js blocked";
        }
    });
})();
