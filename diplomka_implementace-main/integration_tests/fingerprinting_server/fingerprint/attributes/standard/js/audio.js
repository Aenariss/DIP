(function() {
    api.register("audio", function () {
        return new Promise((resolve, reject) => {
            function waitForPlayButton() {
                return new Promise((innerResolve, innerReject) => {
                    let playButton = document.getElementById("play");
                    if (playButton) {
                        playButton.addEventListener("click", () => {
                            function checkElementsAvailability() {
                                let channelDataResult = document.getElementById("channel_data_result");
                                let channelDataResult2 = document.getElementById("channel_data_result2");
                                
                                let copyResult = document.getElementById("copy_result");
                                let copyResult2 = document.getElementById("copy_result2");

                                let byteFrequencyResult = document.getElementById("byte_frequency_result");
                                let floatFrequencyResult = document.getElementById("float_frequency_result");
                                
                                let byteTimeResult = document.getElementById("byte_time_result");
                                let floatTimeResult = document.getElementById("float_time_result");
                                
                                
                                if (channelDataResult.innerHTML != '' && copyResult.innerHTML != '' ) {
                                    var audio_data = {
                                        "channelDataResult" : channelDataResult.innerHTML.split(','),
                                        "channelDataResult2" : channelDataResult2.innerHTML.split(','),

                                        "copyResult" : copyResult.innerHTML.split(','),
                                        "copyResult2" : copyResult2.innerHTML.split(','),

                                        
                                        "byteFrequencyResult" : byteFrequencyResult.innerHTML.split(','),
                                        "floatFrequencyResult" : floatFrequencyResult.innerHTML.split(','),

                                        "byteTimeResult": byteTimeResult.innerHTML.split(','),
                                        "floatTimeResult": floatTimeResult.innerHTML.split(',')
                                        
                                    };
                                    
                                    const result = {
                                        name: 'audio',
                                        data: audio_data
                                    };
                                    
                                    resolve(result);  
                                } else {
                                    setTimeout(checkElementsAvailability, 2500);
                                }
                            }

                            checkElementsAvailability();
                        });

                        innerResolve();
                    } else {

                        setTimeout(waitForPlayButton, 1000); 
                    }
                });
            }

            waitForPlayButton().catch(error => {
                resolve(error); 
            });
        });
    });
})();
