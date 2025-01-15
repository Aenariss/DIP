(function() {
    api.register("navigator", function () {
        try {
            var results = {
                'userAgent': window.navigator.userAgent,
                'appVersion': window.navigator.appVersion,
                'platform': window.navigator.platform,
                'vendor': window.navigator.vendor,
                'language': window.navigator.language,
                'languages': window.navigator.languages,
                'cookieEnabled': window.navigator.cookieEnabled,
                'doNotTrack': window.navigator.doNotTrack,
                'oscpu': window.navigator.oscpu,
                'plugins': Array.from(navigator.plugins).map(({filename,name,description}) => ({filename,name,description})),
                'mimeTypes': Array.from(navigator.mimeTypes).map(a => ({
                    'type': a.type,
                    'description': a.description,
                    'suffixes': a.suffixes,
                    'enabledPlugin': a.enabledPlugin ? a.enabledPlugin.name : null
                }))
            };
            
            return results;
        } catch (e) {
            return "error";
        }
    });
})();
