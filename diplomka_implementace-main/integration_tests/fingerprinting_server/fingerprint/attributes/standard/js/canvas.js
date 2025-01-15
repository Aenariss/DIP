(function() {
    api.register("canvas",  function () {
        try {
            var startTime = performance.now();
            var canvasData = {
                'dataURL': '0',
                'imageData': '0',
                'spoof': false,
                'pointInPath': null,
                'pointInStroke': null,
                'timeTaken': null
            };

            const buttonsContainer = document.getElementById('canvas1-buttons-wrap');

		    const buttons = buttonsContainer.getElementsByTagName('button');
		    const buttonsArray = Array.from(buttons);

		    buttonsArray.forEach(button => {
			    if (button.textContent.trim() === "Add line to canvas" || button.textContent.trim() === "Add circle to canvas" || button.textContent.trim() === "Add text to canvas") {
				        button.click();
			        }
		    });
		
		    const drawon = document.getElementById('getData');
		    drawon.click();

            var img = document.getElementById("fp-image");
		    
            var canvasx = document.getElementById('canvasx');
            var canvas1 = document.getElementById('canvas1');

            var canvasContext = canvasx.getContext("2d");

            canvasContext.drawImage(img, 0, 0);

            
            canvasData.dataURL = canvasx.toDataURL();
     
            canvasData.imageData = canvasContext.getImageData(0, 0, canvasx.width, canvasx.height).data;
            canvasData.spoof = !canvas1.getContext('2d').getImageData(0, 0, canvas1.width, canvas1.height).data.some(channel => channel !== 255);           
            

            var canvas4 = document.getElementById('canvas4');

            try {
                var ret = true;
                var ctx4 = canvas4.getContext('2d')
                const circle = new Path2D();circle.arc(100, 75, 50, 0, 2 * Math.PI);
                for (var i = 0; i < 200; i++) {
                    ret = ret && ctx4.isPointInPath(circle, 100, 100)
                }
                canvasData.pointInPath = ret;
            } catch (e) {
                canvasData.pointInPath = "error";
            }

            var canvas5 = document.getElementById('canvas5');

            try {
                var ret = true;
                var ctx5 = canvas5.getContext('2d')
                const ellipse = new Path2D(); ellipse.ellipse(100, 75, 40, 60, Math.PI * .25, 0, 2 * Math.PI);
                ctx5.lineWidth = 20;
                for (var i = 0; i < 200; i++) {
                    ret = ret && ctx5.isPointInStroke(ellipse, 100, 25)
                }
                canvasData.pointInStroke = ret;
  

            } catch(e) {
                canvasData.pointInStroke = "error";
            }

        } catch(e){
            canvasData = "Not supported";
        }
        var endTime = performance.now();
        canvasData.timeTaken = endTime - startTime;
        return canvasData;
    });
})();
