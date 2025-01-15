
BigInt.prototype.toJSON = function() { 
    return this.toString() + "n"; 
  }; 

function deepEqual(a, b) {
    try { 
        let jsona = JSON.stringify(a);
        let jsonb = JSON.stringify(b);
        if (a === b || jsona === jsonb) { 
            return true;
        } 
        else { 
            return false;
        } 
    } 
    catch (e) { 
        return "error" + e;
    } 
}

function test_worker_basic(){
    try {
        var worker = new Worker('');

        var isWorkerRemoved = deepEqual(worker, undefined);
        
        var onMessage = deepEqual(worker.onmessage, null);
        var onError = deepEqual(worker.onerror, null);

        var onMessageError = deepEqual(worker.onmessageerror, null);
        var eventListener = deepEqual(typeof worker.addEventListener, "function");

        var postMessage = deepEqual(typeof worker.postMessage, "function");
        var removeEventListener = deepEqual(typeof worker.removeEventListener, "function");
        var terminate = deepEqual(typeof worker.terminate, "function");

        var workerTest = {
            "isWorkerRemoved": isWorkerRemoved,
            "onMessage": onMessage,
            "onError": onError,
            "onMessageError": onMessageError,
            "eventListener": eventListener,
            "postMessage": postMessage,
            "removeEventListener": removeEventListener,
            "terminate": terminate
        } 

        worker.terminate();
        return workerTest;

    } catch(e) {
        var workerTest = {
            "isWorkerRemoved": true,
            "onMessage": null,
            "onError": null,
            "onMessageError": null,
            "eventListener": null,
            "postMessage": null,
            "removeEventListener": null,
            "terminate": null
        } 
        return workerTest;
    }

}

/*

function test_worker_implements_dispatchEvent(){
    var worker = new Worker("");
    var workerDispatch = deepEqual(typeof worker.dispatchEvent, "function");
    return workerDispatch;
}



function test_worker_check_communication_handler() {
    return new Promise((resolve, reject) => {
        var worker = new Worker('data:text/javascript;base64,' + btoa('onmessage = function(e) {const result = e.data[0] * e.data[1];postMessage(result);}'));
        worker.onmessage = function(e) {
            resolve(e.data);
            worker.terminate(); //
        };
        worker.onerror = function(error) {
            resolve(error); 
            worker.terminate(); // 
        };
        worker.postMessage([5, 8]);
    });
}

function test_worker_error(){
    return new Promise((resolve, reject) => {
        var worker = new Worker('data:text/javascript;base64,' + btoa('onmessage = function(e) {postMessage(variabledoesnotexist_and_it_is_intentional);}'));
        worker.onmessage = function(e) {
            resolve(1);
            worker.terminate(); 
        };
        worker.onerror = function() {
            resolve(-1); 
            worker.terminate(); 
        };
        worker.postMessage([6,7]);
    });
}

function test_worker_check_communication_listener() {
    return new Promise((resolve, reject) => {
        var worker = new Worker('data:text/javascript;base64,' + btoa('onmessage = function(e) {const result = e.data[0] * e.data[1];postMessage(result);}'));
        worker.addEventListener("message", function(e) {
            resolve(e.data);
            worker.terminate();
        });
        worker.onerror = function(error) {
            resolve(error);
            worker.terminate();
        };
        worker.postMessage([4, 5]);
    });
}
*/

async function test_worker_terminate(){
    try {
        return new Promise((resolve, reject) => {
            var worker = new Worker(('data:text/javascript;base64,' + btoa('onmessage = function(e) {const result = e.data[0] * e.data[1];postMessage(result);}')));
            worker.terminate();

            worker.addEventListener("message", function(e) {
                resolve(e.data);
                worker.terminate();
            });
            worker.onerror = function(error) {
                resolve(null);
                worker.terminate();
            };
            worker.postMessage([7,6]);
        });
    } catch(e) {
        return null;
    }
}
/*
function test_worker_dispatchEvent(){
    var correct_order_check = 1;
    var test_event = new Event("test");
    var worker = new Worker('data:text/javascript;base64,' + btoa(''));

    worker.ontest = function() {
         correct_order_check *= 2;
    };

    worker.addEventListener("test", function(e) {
        correct_order_check *= 3;
    });

    worker.addEventListener("test", function(e) {
        correct_order_check *= 5;
    });

    worker.addEventListener("test", function(e) {
        correct_order_check *= 7;
    });
    worker.dispatchEvent(test_event);

    var workerDispatchEvent = deepEqual(correct_order_check, 105);
    return workerDispatchEvent;
}
*/

(function() {
    api.register("worker", function () {
        try {

            var workerBasics = test_worker_basic();

            //var workerImplementsDispatchEvent = test_worker_implements_dispatchEvent()

            //var workerCheckCommunicationHandlerRes = await test_worker_check_communication_handler();
            //var workerCheckCommunicationHandler = deepEqual(workerCheckCommunicationHandlerRes, 40);

            //var workerErrorRes = await test_worker_error();
            //var workerError = deepEqual(workerErrorRes, -1);

            //var workerCheckCommunicationListenerRes = await test_worker_check_communication_listener();
            //var workerCheckCommunicationListener = deepEqual(workerCheckCommunicationListenerRes, 20);

            //var workerTerminateRes = await test_worker_terminate();
            //var workerTerminate = deepEqual(workerTerminateRes, 0);

            //var workerDispatchEvent = test_worker_dispatchEvent();

            const result = {
                "workerBasics": workerBasics
                //"workerImplementsDispatchEvent": workerImplementsDispatchEvent,
                //"workerCheckCommunicationHandler": workerCheckCommunicationHandler,
                //"workerError": workerError,
                //"workerCheckCommunicationListener": workerCheckCommunicationListener,
                
                //"workerDispatchEvent": workerDispatchEvent,
                //"workerTerminate": workerTerminate
            }

            return result;


        } catch (e) {

            return "error" + e;
        }
    });
})();

