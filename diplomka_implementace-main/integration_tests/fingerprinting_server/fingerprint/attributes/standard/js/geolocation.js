(function() {
    async function getGeolocation() {
        if (typeof navigator.geolocation === 'undefined') {
            const data = {
                accuracy: null,
                altitude: null,
                altitudeAccuracy: null,
                heading: null,
                latitude: null,
                longitude: null,
                speed: null,
                timestamp: null,
                valid: true,
                info: "addon blocked geolocation"
            };

            const result = {
                name: 'geolocation',
                data: data
            };

            return result;
        }
        return new Promise((resolve, reject) => {
            if ('geolocation' in navigator) {

                navigator.geolocation.getCurrentPosition(
                    position => {
                        const data = {
                            accuracy: position.coords.accuracy,
                            altitude: position.coords.altitude,
                            altitudeAccuracy: position.coords.altitudeAccuracy,
                            heading: position.coords.heading,
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            speed: position.coords.speed,
                            timestamp: position.timestamp,
                            valid: true,
                            info: "successful callback"
                        };

                        const result = {
                            name: 'geolocation',
                            data: data
                        };

                        resolve(result);
                    },
                    error => {
                        const data = {
                            accuracy: null,
                            altitude: null,
                            altitudeAccuracy: null,
                            heading: null,
                            latitude: null,
                            longitude: null,
                            speed: null,
                            timestamp: null,
                            valid: false,
                            info: "error resolving GPS data " + error.message
                        };
                        resolve({
                            name: 'geolocation',
                            data: data
                        });
                    },
                    {   
                        timeout: 20000, 
                        maximumAge: 0
                    }
                );
            } else {
                const data = {
                    accuracy: null,
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    latitude: null,
                    longitude: null,
                    speed: null,
                    timestamp: null,
                    valid: false,
                    info: "geolocation not supported in this browser"
                };

                const result = {
                    name: 'geolocation',
                    data: data
                };

                resolve(result);
            }
        });
    }

    api.register("geolocation", async function() {
        const result = await getGeolocation();
        return result;
    });
})();
