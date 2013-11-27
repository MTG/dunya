$(document).ready(function() {
     audio = $("#theaudio")[0];
     renders = $('#renders');
     rendersMask = $('#rendersMask');
     capcal = $('#capcal');
     capcalTotal = $('#capcalTotal');
     renderTotal = $('#renderTotal');
     zoomFactor = "";
     waveform = $('#bigWave img');
     plButton = $("#control .plButton");
     timecode = $("#timecode");
     zooms = $(".zoom");
	/* waveform.click(function(e) {
	 	var offset_l = $(this).offset().left - $(window).scrollLeft();
		var left = Math.round( (e.clientX - offset_l) );
	    mouPlay(left);
	});*/
     loaddata();
});

function loaddata() {
    // We do pitch track with manual httprequest, because
    // we want typedarray access
    var oReq = new XMLHttpRequest();
    oReq.open("GET", pitchtrackurl, true);
    oReq.responseType = "arraybuffer";
    oReq.onload = function(oEvent) {
        if (oReq.status == 200) {
            var arrayBuffer = oReq.response;
            var view = new Uint8Array(arrayBuffer);
            console.debug( "manual!");
            console.debug(view.length);
            var canvas = $("#thecanvas")[0];
            canvas.width = 900;
            canvas.height = 256;
            var context = canvas.getContext("2d");
            context.translate(0.5, 0.5);
            var waszero = false;
            for (var i = 0; i < 900; i++) {
                var tmp = 255-view[i*4];
                // We choose 0 if the pitch is unknown, or 255 if it's
                // higher than the 3 octaves above tonic. If so, we don't
                // want to draw something, just skip until the next value
                if (tmp == 0 || tmp == 255) {
                    waszero = true;
                    context.moveTo(i, tmp);
                } else {
                    if (waszero) {
                        waszero = false;
                        context.moveTo(i, tmp);
                    } else {
                        context.lineTo(i, tmp);
                    }
                }
            }
            context.lineWidth = 2;
            context.stroke();
            context.beginPath();
            context.moveTo(0, 128);
            context.lineTo(900, 128);
            context.moveTo(0, 192);
            context.lineTo(900, 192);
            context.stroke();
        }
    };
    oReq.send();
    $.ajax(histogramurl, {dataType: "json", type: "GET", 
        success: function(data, textStatus, xhr) {
            console.debug("data!");
            console.debug(data.length);
            var histogram = $("#histogramcanvas")[0];
            histogram.width = 200;
            histogram.height = 256;
            var context = histogram.getContext("2d");
            context.translate(0.5, 0.5);
            var max = 0;
            for (var i = 0; i < data.length; i++) {
                if (data[i] > max) {
                    max = data[i];
                }
            }
            var factor = 150 / max;
            for (var i = 0; i < data.length; i++) {
                v = data[i] * factor;
                context.lineTo(200-v, 256-i);
            }
            context.lineWidth = 2;
            context.stroke();

    }});

}

function mouPlay(desti){
	posicio = renders.position();
	distclick = Math.abs(posicio.left)+desti;
	percentPunt = (distclick*100)/(waveform.width());
	nouPunt = (audio.duration*percentPunt)/100;
	console.log(nouPunt+" - "+audio.duration);
	audio.pause();
	audio.currentTime = Math.ceil(nouPunt);
	audio.play();
	audio.currentTime = Math.ceil(nouPunt);
}
function play() {
    audio.play();
    int = window.setInterval(updateProgress, 30);
}
function pause() {
    audio.pause();
    window.clearInterval(int);
}
function updateProgress() {
    progress_seconds = Math.ceil(audio.currentTime);
    progress_minutes = Math.floor(audio.currentTime/60);
    resto = (progress_seconds-(progress_minutes*60));
    if(resto<10){
		resto = "0"+resto;
    }
    if(progress_minutes<10){
		progress_minutes = "0"+progress_minutes;
    }
    progress_percent = (audio.currentTime / audio.duration * 100);
	ampleMask = rendersMask.width();
	ampleRenders = renders.width();
	ampleRenderTotal = renderTotal.width();
    $('#progress_seconds').html('Seconds: ' + progress_seconds);
    $('#progress_seconds').html('Seconds: ' + ampleRenders);
    nouLeft = ((ampleRenders*progress_percent)/100);
    nouLeft2 = ((ampleRenderTotal*progress_percent)/100);
    capcal.css('left',nouLeft);
    capcalTotal.css('left',nouLeft2);

    if(nouLeft>(ampleMask/2)){
    	decalatge = (nouLeft-(ampleMask/2))*(-1);
	    renders.css('left',decalatge);
    }
    timecodeHtml = ""+progress_minutes+":"+resto;
    timecode.html(timecodeHtml);
};
function zoom(factor){
	//zoomFactor = factor;
	//renders.width((factor*901));
	//zooms.removeClass("selected");
	//$("#zoom"+factor).addClass("selected");
}
function playrecord(){
	if(plButton.hasClass("stop")){
		pause();
		plButton.removeClass("stop");
	}else{
		play();
		plButton.addClass("stop");
	}
}

