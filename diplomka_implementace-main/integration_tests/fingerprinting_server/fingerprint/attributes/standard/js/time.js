function getTimeWithDelay() {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            let d = new Date();
            resolve(d.getMilliseconds());
        }, Math.floor(Math.random() * 2000) + 1000); 
    });
}

async function startIterations() {
    let milliseconds = [];
    for (let i = 0; i < 3; i++) {
        milliseconds.push(await getTimeWithDelay());
    }
    return milliseconds;
}

(function() {
    api.register("time", function () {
        return new Promise((resolve, reject) => {
            try {
                startIterations().then(milliseconds => {
                    var result = {
                        'name': 'time',
                        'data': milliseconds
                    };
                    resolve(result);
                }).catch(error => {
                    resolve("error" + error);
                });
            } catch (e) {
                console.log(e)
                resolve("error" + e);
            }
        });
    });
})();
