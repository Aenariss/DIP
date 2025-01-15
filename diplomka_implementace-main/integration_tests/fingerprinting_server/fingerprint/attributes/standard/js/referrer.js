(function() {

    api.register("referrer", function() {
        try {
            var referrer = document.referrer;
            return referrer;
        } catch (error) {
            console.log(e)
            return "error: " + error;
        }
    });
})();
