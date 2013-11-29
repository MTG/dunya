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

function spectrogram(context, view) {
    console.debug(view.length);
    var waszero = false;
    context.moveTo(0, 10);
    context.lineTo(10, 10);
    context.moveTo(0,0);
    for (var i = 0; i < 900; i++) {
        var tmp = 255-view[i*8];
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

function plothistogram(data) {
    var histogram = $("#histogramcanvas")[0];
    histogram.width = 200;
    histogram.height = 256;
    var context = histogram.getContext("2d");
    context.moveTo(180, 10);
    context.lineTo(200, 10);
    context.moveTo(200, 256);
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
}

function plotpitch(request) {
    // In order to account for slow internet connections,
    // we always load one image ahead of what we need.
    // TODO: We need to know when the last image is.
    var spec = new Image();
    spec.src = specurl;
    var arrayBuffer = request.response;
    var view = new Uint8Array(arrayBuffer);
    var canvas = $("#pitchcanvas")[0];
    canvas.width = 900;
    canvas.height = 256;
    var context = canvas.getContext("2d");
    spec.onload = function() {
        context.drawImage(spec, 0, 0);
        spectrogram(context, view);
    }
}

function drawwaveform(tempo, ticks) {
    var wave = new Image();
    wave.src = waveformurl;
    var canvas = $("#rhythmcanvas")[0];
    canvas.width = 900;
    canvas.height = 256;
    var context = canvas.getContext("2d");
    wave.onload = function() {
        context.drawImage(wave, 0, 0);
        plotticks(context, ticks);
        plottempo(context, tempo);
    }
}

function plotticks(context, data) {
    data.sort();
    from = data[0];
    to = data[data.length-1];
    // TODO: make this into minutes/seconds
    $("#pulseFrom").html(from);
    $("#pulseTo").html(to);

    // TODO: Don't draw if the tickbox is off
    // TODO: Only draw on 3x and 4x zoom

}

function plottempo(context, data) {
    var low = 1;
    var high = 0;
    for (var i = 0; i < data.length; i++) {
        var val = data[i][1];
        if (val > high) {
            high = val;
        }
        if (val < low) {
            low = val;
        }
    }
    high = high * 1.2;
    low = low * 1.2;
    var factor = 128 / (high - low);

    var secPerPixel = 900 / 32;
    for (var i = 0; i < data.length; i++) {
        var x = data[i][0] * secPerPixel; // Data points are every 0.5 seconds
        if (x > 900) {
            break;
        }
        var y = (data[i][1]-low) * factor;
        console.debug(data[i][0]+","+data[i][1]);
        context.lineTo(x, 256-y);
    }
    context.strokeStyle = "#eee";
    context.lineWidth = 2;
    context.stroke();
}

function loaddata() {
    // We do pitch track with manual httprequest, because
    // we want typedarray access
    var oReq = new XMLHttpRequest();
    oReq.open("GET", pitchtrackurl, true);
    oReq.responseType = "arraybuffer";
    oReq.onload = function(oEvent) {
        if (oReq.status == 200) {
            plotpitch(oReq);
        }
    };
    oReq.send();
    $.ajax(histogramurl, {dataType: "json", type: "GET", 
        success: function(data, textStatus, xhr) {
            plothistogram(data);
    }});

    var ticksDone = false;
    var tempoDone = false;

    $.ajax(rhythmurl, {dataType: "json", type: "GET", 
        success: function(data, textStatus, xhr) {
            tickData = data;
            ticksDone = true;
            drawwave();
    }});

    $.ajax(aksharaurl, {dataType: "json", type: "GET", 
        success: function(data, textStatus, xhr) {
            tempoData = data;
            tempoDone = true;
            drawwave();
    }});

    function drawwave() {
        if (ticksDone && tempoDone) {
            drawwaveform(tempoData, tickData);
        }
    }

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
    progress_percent = (audio.currentTime / 32 * 100);
	ampleMask = rendersMask.width();
	ampleRenders = renders.width();
	ampleRenderTotal = renderTotal.width();
    nouLeft = ((ampleRenders*progress_percent)/100);
    nouLeft2 = ((ampleRenderTotal*progress_percent)/100);
    capcal.css('left',nouLeft);
    capcalTotal.css('left',nouLeft2);

    //if(nouLeft>(ampleMask/2)){
    //	decalatge = (nouLeft-(ampleMask/2))*(-1);
	 //   renders.css('left',decalatge);
    //}
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

