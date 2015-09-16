$(document).ready(function() {
     hasfinished = false;
     pagesound = ""
     audio = $("#theaudio")[0];
     renders = $('#renders');
     rendersMask = $('#rendersMask');
     capcal = $('#capcal');
     capcalTotal = $('#capcalTotal');
     renderTotal = $('#renderTotal');
     zoomFactor = "";
     waveform = $('#renderTotal canvas');
     plButton = $("#control .plButton");
     timecode = $("#timecode");
     zooms = $(".zoom");
     // What point in seconds the left-hand side of the
     // image refers to.
     beginningOfView = 0;
     // The 900 pitch values currently on screen
     pitchvals = new Array(900);
	 waveform.click(function(e) {
	 	var offset_l = $(this).offset().left - $(window).scrollLeft();
		var left = Math.round( (e.clientX - offset_l) );
	    mouPlay(left);
	 });
     waveform.mouseenter(function(e) {
         if (pagesound && pagesound.duration) {
             waveform.css("cursor", "pointer");
         } else {
             waveform.css("cursor", "wait");
         }
     });
     waveform.mousemove(function(e) {
         if (pagesound && pagesound.duration) {
             var offset_l = $(this).offset().left - $(window).scrollLeft();
             var left = Math.round( (e.clientX - offset_l) );
             var miniviewWidth = renderTotal.width();
             var miniviewPercent = left / miniviewWidth;
             var timeseconds = Math.floor(recordinglengthseconds * miniviewPercent);

             $("#timepoint").html(formatseconds(timeseconds));
             $("#timepoint").show();
             var offset = $("#renderTotal").offset();
             $("#timepoint").css({
                 "top" : e.pageY - offset.top,
                 "left" : e.pageX - offset.left + 15
             });
        }
     });
     waveform.mouseleave(function() {
        $("#timepoint").hide();
     });
     $(".zoom").click(function(e) {
         e.preventDefault();
         // Remove selected
         $(".zoom").removeClass("selected");
         // Find all zooms with all our classes (e.g. 'zoom zoom<n>')
         // and apply 'selected'
         var zclasses = $(this).attr("class");
         $("[class='"+zclasses+"']").addClass("selected");
         var level = $(this).data("length");
         zoom(level);
     });
     loaddata();

     $("#showRhythm").click(function(e) {
        //drawwaveform();
     });

     soundManager.onready(function() {
         pagesound = soundManager.createSound({
               url: audiourl,
         });
     });

     $(document).keypress(function(e) {
         // The Space key is play/pause unless in the searchbox
         if ((e.keyCode == 0 || e.keyCode == 32) && !$(e.target).is("#searchbox")) {
             e.preventDefault();
             playrecord();
         }
     });
});

function plotsa(context) {
    // Sa and sa+1 line.
    context.beginPath();
    // sa+1, dotted
    context.moveTo(0, 128);
    for (var i = 0; i < 900; i+=10) {
        context.moveTo(i, 128.5);
        context.lineTo(i+5, 128.5);
    }
    // sa, solid
    context.moveTo(0, 192.5);
    context.lineTo(900, 192.5);
    context.strokeStyle = "#eee";
    context.lineWidth = 1;
    context.stroke();
    context.closePath()
}

function spectrogram(context, view) {
    plotsa(context);
    var waszero = false;
    context.moveTo(0, 10);
    context.lineTo(10, 10);
    context.moveTo(0,0);
    var skip = secondsPerView / 4;
    // Start is in samples
    var start = (beginningOfView / secondsPerView) * 900 * skip;
    // Number of pixels we draw
    var end = Math.min(900+start, start+(view.length-start)/skip);
    var remaining = view.length-start;
    //console.debug("length " + view.length);
    //console.debug(remaining + " samples remaining");
    //console.debug("with skip, " + (remaining/skip) + " rem");
    //console.debug("skip " + skip);
    //console.debug("draw from " + start + " to " + end);
    context.beginPath();
    for (var i = start; i < end; i++) {
        // Find our point
        var xpos = i-start;
        var dataindex = start + xpos*skip;
        var data = view[dataindex];
        // Invert on canvas
        var tmp = 255-data;
        //console.debug(" at ("+xpos+","+tmp+") data " + dataindex);
        // We choose 0 if the pitch is unknown, or 255 if it's
        // higher than the 3 octaves above tonic. If so, we don't
        // want to draw something, just skip until the next value
        if (tmp == 0 || tmp == 255) {
            waszero = true;
            context.moveTo(xpos, tmp);
        } else {
            if (waszero) {
                waszero = false;
                context.moveTo(xpos, tmp);
            } else {
                context.lineTo(xpos, tmp);
            }
        }
        // Set the pitchvals so we can draw the histogram
        pitchvals[xpos] = tmp;
    }

    //context.strokeStyle = "#e71d25";
    context.strokeStyle = "#eee";
    context.lineWidth = 2;
    context.stroke();
    context.closePath();
}
 
 
function plotscore() {
    // In order to account for slow internet connections,
    // we always load one image ahead of what we need.
    // TODO: We need to know when the final image is.
    var spec = new Image();
    spec.src = scoreurl;
    //var view = new Uint8Array(pitchdata);
    var canvas = $("#scorecanvas")[0];
    canvas.width = 900;
    canvas.height = 256;
    var context = canvas.getContext("2d");
    spec.onload = function() {
        context.drawImage(spec, -30, -30, 900, 1200);
        //spectrogram(context, view);
    }
}
      
function plotpitch() {
    // In order to account for slow internet connections,
    // we always load one image ahead of what we need.
    // TODO: We need to know when the final image is.
    var spec = new Image();
    spec.src = specurl;
    var view = new Uint8Array(pitchdata);
    var canvas = $("#pitchcanvas")[0];
    canvas.width = 900;
    canvas.height = 256;
    var context = canvas.getContext("2d");
    spec.onload = function() {
        context.drawImage(spec, 0, 0);
        spectrogram(context, view);
    }
}

function plotsmall() {
    var pxpersec = 900.0/recordinglengthseconds;
    var smallFill = function(data, colour) {
        context.fillStyle = colour;
        for (var i = 0; i < data.length; i++) {
            var d = data[i];
            var txt = d[0];
            var s = d[1];
            var e = d[2];
            if($.type(colour) === "string") {
                context.globalAlpha = 0.5;
                context.fillStyle = colour;
            } else {
                var col = colour[txt];
                context.globalAlpha = 1;
                context.fillStyle = col;
            }
            var spos = Math.round(s * pxpersec)+0.5;
            var epos = Math.round(e * pxpersec)+0.5;
            context.fillRect(spos, 0, epos-spos, 64);
        }
    };
    var small = new Image();
    small.src = smallurl;
    var canvas = $("#smallcanvas")[0];
    canvas.width = 900;
    canvas.height = 64;
    var context = canvas.getContext("2d");
    small.onload = function() {
        context.drawImage(small, 0, 0, 900, 64, 0, 0, 900, 64);
        //smallFill(banshidata, banshicolours);
        //smallFill(luogudata, "#0f0");
    }
    
    // Draw zones on smallcanvas
    //example = { 'zonex': { 'init': 10.0,'end':30.0}, 'zoney': {'init': 100.0, 'end':145.0}}
    example2 = [[ 'a', 10.0, 30.0 ], ['b', 100.0, 145.0]]
    smallFill(example2, "#0ff");

}

function drawwaveform() {
    var wave = new Image();
    wave.src = waveformurl;
    var canvas = $("#histogramcanvas")[0];
    canvas.width = 900;
    canvas.height = 256;
    var context = canvas.getContext("2d");
    wave.onload = function() {
        context.drawImage(wave, 0, 0);
    }
}

function sortNumber(a,b) {
    return a - b;
}

function loaddata() {
    // We do pitch track with manual httprequest, because
    // we want typedarray access

    pitchDone = false;
    var oReq = new XMLHttpRequest();
    oReq.open("GET", pitchtrackurl, true);
    oReq.responseType = "arraybuffer";
    oReq.onload = function(oEvent) {
        if (oReq.status == 200) {
            pitchdata = oReq.response;
            pitchDone = true;
            dodraw();
        }
    };
    oReq.send();

    var ticksDone = false;
   
    function dodraw() {
        if (pitchDone ) {
            drawdata();
        }
    }
    
}

function drawdata() {
    //drawwaveform();
    plotpitch();
    plotsmall();
    plotscore();
    var start = beginningOfView;
    var skip = secondsPerView / 4;
    $(".timecode1").html(formatseconds(start));
    $(".timecode2").html(formatseconds(start+skip));
    $(".timecode3").html(formatseconds(start+skip*2));
    $(".timecode4").html(formatseconds(start+skip*3));
    $(".timecode5").html(formatseconds(start+skip*4));

    // The highlighted miniview
    var beginPercentage = (beginningOfView/recordinglengthseconds);
    var endPercentage = (beginningOfView+secondsPerView) / recordinglengthseconds;

    var beginPx = renderTotal.width() * beginPercentage;
    var endPx = renderTotal.width() * endPercentage;
    var mini = $('#miniviewHighlight');
    mini.css('left', beginPx);
    mini.css('width', endPx-beginPx);
}

function mouPlay(desti){
    percent = desti/waveform.width();
    clickseconds = recordinglengthseconds * percent

    posms = clickseconds * 1000;
    part = Math.ceil(clickseconds / secondsPerView);
    // Update the internal position counter (counts from 0, part counts from 1)
    beginningOfView = (part - 1) * secondsPerView;

    if (pagesound && pagesound.duration) {
        // We can only set a position if it's fully loaded
        var wasplaying = !pagesound.paused;
        if (wasplaying) {
            pagesound.pause();
        }
        pagesound.setPosition(posms);
        replacepart(part);
        updateProgress();
        if (wasplaying) {
            pagesound.resume();
        }
    }
}

function play() {
    if (hasfinished) {
        hasfinished = false;
        replacepart(1);
        beginningOfView = 0;
        drawdata();
    }
    pagesound.play({onfinish: function() {
        window.clearInterval(int);
        plButton.removeClass("stop");
        hasfinished = true;
    }});
    int = window.setInterval(updateProgress, 30);
}
function pause() {
    pagesound.pause();
    window.clearInterval(int);
}

function formatseconds(seconds) {
    progress_seconds = Math.ceil(seconds);
    progress_minutes = Math.floor(seconds/60);
    resto = (progress_seconds-(progress_minutes*60));
    // never show :60 in seconds part
    if (resto >= 60) {
        resto = 0;
        progress_minutes += 1;
    }
    if(resto<10){
		resto = "0"+resto;
    }
    if(progress_minutes<10){
		progress_minutes = "0"+progress_minutes;
    }
    timecodeHtml = ""+progress_minutes+":"+resto;
    return timecodeHtml;
}

function replacepart(pnum) {
    waveformurl = waveformurl.replace(/part=[0-9]+/, "part="+pnum);
    specurl = specurl.replace(/part=[0-9]+/, "part="+pnum);
    drawdata();
}

function updateProgress() {
    var currentTime = pagesound.position / 1000;
    // formatseconds appears to run 1 second ahead of time,
    // so correct for it here
    formattime = formatseconds(currentTime-1);
    progress_percent = (currentTime-beginningOfView) / secondsPerView * 100;
    total_progress_frac = (currentTime/recordinglengthseconds);
	ampleMask = rendersMask.width();
	ampleRenders = renders.width();
	ampleRenderTotal = renderTotal.width();
    leftLargeView = ((ampleRenders*progress_percent)/100);
    leftSmallView = ampleRenderTotal*total_progress_frac;
    capcal.css('left', leftLargeView-5);
    capcalTotal.css('left', leftSmallView-6);

    if (leftLargeView > 900) {
        beginningOfView = Math.floor(currentTime / secondsPerView) * secondsPerView;
        pnum = Math.floor(beginningOfView / secondsPerView + 1);
        replacepart(pnum)
    }
    timecode.html(formattime + "<span>"+recordinglengthfmt+"</span>");
};

function zoom(level){
    secondsPerView = level;
    waveformurl = waveformurl.replace(/waveform[0-9]{1,2}/, "waveform"+level);
    specurl = specurl.replace(/spectrum[0-9]{1,2}/, "spectrum"+level);
    // When we go from a zoomed in to a zoomed out size,
    // we need to make sure that `beginningOfView` is on an
    // image boundary
    beginningOfView = Math.floor(beginningOfView / secondsPerView);
    pnum = Math.floor(beginningOfView / secondsPerView + 1);
    waveformurl = waveformurl.replace(/part=[0-9]+/, "part="+pnum);
    specurl = specurl.replace(/part=[0-9]+/, "part="+pnum);
    drawdata();

}


