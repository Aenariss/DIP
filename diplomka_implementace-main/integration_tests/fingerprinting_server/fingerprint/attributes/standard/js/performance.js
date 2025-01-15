function getPerformanceWithDelay() {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            let p = window.performance.now();
            resolve(p);
        }, Math.floor(Math.random() * 2000) + 1000); 
    });
}

async function startPerformanceIterations() {
    let performance = [];
    for (let i = 0; i < 3; i++) {
        performance.push(await getPerformanceWithDelay());
    }
    return performance;
}

(function() {
    api.register("performance", function () {
        return new Promise((resolve, reject) => {
            try {
                startPerformanceIterations().then(performance => {
                    var result = {
                        'name': 'performance',
                        'data': performance
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