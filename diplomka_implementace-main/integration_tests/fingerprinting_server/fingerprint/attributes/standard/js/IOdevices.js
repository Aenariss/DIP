(function() {
    api.register("io_devices", function() {
        return new Promise((resolve, reject) => {
            navigator.mediaDevices.enumerateDevices()
                .then(devices => {
                        const result = {
                            name: 'io_devices',
                            data: devices
                        };
                        resolve(result);                 
                })
                .catch(error => {
                    const result = {
                        name: 'io_devices',
                        data: 'ERROR' + error
                    };
                    resolve(result);
                });

            setTimeout(() => {
                const result = {
                    name: 'io_devices',
                    data: 'ERROR timeout'
                };
                resolve(result);
            }, 10000);
        });
    });
})();
