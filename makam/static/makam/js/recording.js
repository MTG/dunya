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
     currentSymbtrIndex = 1;
     currentInterval = 1;
     currentPage = 0;
     lastOffset = null;
     colors = ["#FFC400","#00FFB3","#0099FF","#FF007F","#00FFFF", "#FF000D","#FF9100","#4800FF","#00FF40","#00FF80"]
     images = [];
     startLoaded = 0;
     lastLoaded = 0;
     contextNames = [];
     lastIndex = -1;
     lastpitch = -1; 
     scoreLoaded = false;
     barPages = [];
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
        var sectionName = ''; 
        var rect = waveform[0].getBoundingClientRect();
        var mousePos = e.clientX - rect.left;
     
        for (var i = 0; i < contextNames.length; i++) {
          if (contextNames[i][0] < mousePos && contextNames[i][1]>mousePos){
             sectionName = contextNames[i][2];
          }
        }
        if (pagesound && pagesound.duration) {
             var offset_l = $(this).offset().left - $(window).scrollLeft();
             var left = Math.round( (e.clientX - offset_l) );
             var miniviewWidth = renderTotal.width();
             var miniviewPercent = left / miniviewWidth;
             var timeseconds = Math.floor(recordinglengthseconds * miniviewPercent);

             $("#timepoint").html(formatseconds(timeseconds)+'</br><b>'+sectionName+'</b>');
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

     enabledCurrentPitch = false;
     $('#enable-show-pitch').change(function(){
         enabledCurrentPitch = this.checked ;
         if (enabledCurrentPitch){
             $("#overlap-pitch").show();
             $("#overlap-corrected-pitch").show();
             $("#enable-corrected-pitch").prop('checked', true);
         }else{
             $("#overlap-pitch").hide();
         }
     });
     $("#enable-corrected-pitch").change(function(){
         if (this.checked ){
             $("#overlap-corrected-pitch").show();
         }else{
             $("#overlap-corrected-pitch").hide();
             $('#enable-show-pitch').attr('checked', false);
             enabledCurrentPitch = false ;
             $("#overlap-pitch").hide();
         }
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

function plottonic(context) {
    // Sa and sa+1 line.
    context.beginPath();
    // sa+1, dotted
    var tonicval = 255-tonic;
    context.moveTo(0, tonicval);
    context.lineWidth = 2;
    for (var i = 0; i < 900; i+=10) {
        context.moveTo(i, tonicval);
        context.lineTo(i+5, tonicval);
    }
    context.strokeStyle = "#ffffff";
    context.stroke();
}

function spectrogram(context, view, color) {
    var waszero = false;
    //context.moveTo(0, 10);
    //context.moveTo(0, 10);
    //context.lineTo(10, 10);
    //context.moveTo(0,0);
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
    context.strokeStyle = color[0];
    context.lineWidth = 3;
    context.stroke();
    context.strokeStyle = color[1];
    context.lineWidth = 2;
    context.stroke();
    
    context.closePath();
    plottonic(context);
}

function plotscore(index, color) {
        
    $("#no-score").hide(); 
    $("#score-cont").show(); 
    if (!scoreLoaded ){
        for(var i=1; i<=numbScore;i++){
            $("#score-cont").append('<div class="score-page" id="score-'+i+'"></div>');
        }    
        for(var i=1; i<=numbScore;i++){
            score = scoreurl.replace(/part=[0-9]+/, "part="+i);
            $.ajax(score, {dataType: "text", type: "GET", score:i,
                success: function(data, textStatus, xhr) {
                
                data = data.replace('</svg>','<rect class="marker" x="0" y="0" width="0" height="0" ry="0.0000" style="fill:blue;fill-opacity:0.1;stroke-opacity:0.9" /></svg>');
                
                $("#score-"+this.score).append(data);
                var bars = []
                $("#score-"+this.score).find("rect[width='0.1900'][y='-2.0000'][height='4.0000']").each(function(){
                    var pos = $(this).attr('transform').split("(");
                    var xy = pos[1].split(", ");
                    bars.push([parseInt(xy[0]), parseInt(xy[1]), $(this)]);
                });
                barPages[this.score] = bars;
    
            }, error: function(xhr, textStatus, errorThrown) {
               console.debug("xhr error " + textStatus);
               console.debug(errorThrown);
            }});
        }
        scoreLoaded = true;
        
    }else{
        if (aligns[index]){
          var find = false;
          var curr =   $("a[id^='l" + aligns[index]['line'] + "-f");
          curr.each(function(){
              find = find || highlightNote(index, $(this));             
          });
          if (!find){
            console.log("COULD NOT FIND");
            console.log(index);
          }
        }
    }
}

function disableScore(currentTime){
    if (currentTime > (endPeriod+1) || currentTime < (startPeriod-1)){
        $("#no-score").show(); 
        $("#score-cont").hide(); 
    }
}
function highlightNote(index, note){

    var find = false;
    if(parseInt(note.attr('from')) <= aligns[index]['pos'] && parseInt(note.attr('to')) > aligns[index]['pos']){
        $("a[highlight='1'").attr('highlight','0');
       
        var pos = note.find('path').attr('transform').split("(");
        var xy = pos[1].replace(") scale","").split(',');

        var prev = null;
        var prevmin= Number.MAX_VALUE;
        var prevx = 0;
        var prevy = 0;
        var next = null;
        var nextmin= Number.MAX_VALUE;
        var nextx = 0;
        var nexty = 0;
       
        var page = parseInt(note.closest(".score-page").attr('id').replace("score-",''));
        var bars = barPages[page];
        for(var i=0;i<bars.length; i++){
         if(Math.abs(parseInt(xy[1]) - bars[i][1]) <5 &&  (parseInt(xy[0]) - bars[i][0]) > 0 && prevmin > (parseInt(xy[0])- bars[i][0])){
             prevmin = parseInt(xy[0]) - bars[i][0];
             prev = bars[i][2];
             prevx = bars[i][0];
             prevy = bars[i][1];

         }
         if(Math.abs(parseInt(xy[1]) - bars[i][1]) <5 &&  (bars[i][0] - parseInt(xy[0])) > 0 && nextmin > (bars[i][0] - parseInt(xy[0]))){
             nextmin = bars[i][0] - parseInt(xy[0]) ;
             next = bars[i][2];
             nextx = bars[i][0];
             nexty = bars[i][1];
         }
        }
        note.attr('highlight','1');    
       
        $(".score-page").hide();
        var currScore = $("#score-"+page);
        currScore.show();
        $("#score-"+(page+1)).each(function(){$(this).show()});
        
        var y = -2 * nexty;
        if (nexty > 15){
            
            y = y * 2 ;
        }
        if(next && prev){
           currScore.find('.marker').attr('x',prevx);
           currScore.find('.marker').attr('y', prevy-4);
           currScore.find('.marker').attr('width',nextx-prevx);
           currScore.find('.marker').attr('height',"10");
           currScore.find('.marker').css('fill',colorsNames[aligns[index]['color']]);
           $('#score-cont').css("top", y );
        }else if(next && prev==null){
           currScore.find('.marker').attr('x', 0);
           currScore.find('.marker').attr('y', nexty-4);
           currScore.find('.marker').attr('width',nextx);
           currScore.find('.marker').attr('height',"10");
           currScore.find('.marker').css('fill',colorsNames[aligns[index]['color']]);
           $('#score-cont').css("top", y);
        }
     
        find = true;
    }
    return find;
}

function updateScoreProgress(currentTime){
    if (currentTime > endPeriod || currentTime < startPeriod)
    {
        var updated = false;
        if (lastIndex && aligns.length < (lastIndex + 1)){
            aligns[lastIndex+1]['starttime'];
            if (aligns[lastIndex+1]['starttime']<currentTime && aligns[lastIndex+1]['endtime']>currentTime){
                endPeriod = aligns[lastIndex+1]['endtime'];
                startPeriod = aligns[lastIndex+1]['starttime'];           
                plotscore(lastIndex)   
                lastIndex = lastIndex+1;
                updated = true;
            }
        }
        if(!updated){
            for (var i=0; i<aligns.length; i++){
                if (aligns[i]['starttime']<currentTime && aligns[i]['endtime']>currentTime){
                    endPeriod = aligns[i]['endtime'];
                    startPeriod = aligns[i]['starttime'];
                    color = aligns[i]['color'];
                    plotscore(i, color); 
                    lastIndex = i;
                    return;
                }
            }
        }
        disableScore(currentTime); 
    }
}

function plotpitch() {
    // In order to account for slow internet connections,
    // we always load one image ahead of what we need.
    // TODO: We need to know when the final image is.
    var spec = new Image();
    spec.src = specurl;
    var view = new Uint8Array(pitchdata);
    correctedview = new Uint8Array(correctedpitchdata);
    var canvas = $("#pitchcanvas")[0];
    var correctedCanvas = $("#overlap-corrected-pitch")[0];
    canvas.width = 900;
    canvas.height = 256;
    correctedCanvas.width = 900;
    correctedCanvas.height = 256;
   var context = canvas.getContext("2d");
    var correctedContext = correctedCanvas.getContext("2d");
    spec.onload = function() {
        context.drawImage(spec, 0, 0);
        spectrogram(context, view, ["#E0A3C2", "#CC6699"]);
        spectrogram(correctedContext, correctedview, ["#8A8A8A", "#FFFFFF"]);
    }
}

function plotsmall() {
    var pxpersec = 900.0/recordinglengthseconds;
    var smallFill = function(data, colour, colorsNames) {
        context.fillStyle = colour;
        for (var i = 0; i < data.length; i++) {
            var d = data[i];
            var txt = d['name'];
            var s = d['time'][0];
            var e = d['time'][1];
            context.globalAlpha = 0.3;
            context.fillStyle = colorsNames[txt];

            var spos = Math.round(s * pxpersec)+0.5;
            var epos = Math.round(e * pxpersec)+0.5;
            context.fillRect(spos, 0, epos-spos, 64);
            
            contextNames.push([spos,epos,txt]);
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
    
        

    // Draw sections on smallcanvas
    colorsNames = {};
    currColor = 0;
    for (var i = 0; i < sections.length; i++) {
            var name = sections[i]['name'];
            if (!(name in colorsNames)){
                colorsNames[name]=colors[currColor];
                currColor += 1;
            }
    }
    smallFill(sections, "#0ff", colorsNames);
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

    correctedpitchDone = false;
    var oReq2 = new XMLHttpRequest();
    oReq2.open("GET", correctedpitchurl, true);
    oReq2.responseType = "arraybuffer";
    oReq2.onload = function(oEvent) {
        if (oReq2.status == 200) {
            correctedpitchdata = oReq2.response;
            correctedpitchDone = true;
            dodraw();
        }
    };
    oReq2.send();

    var ticksDone = false;
    var symbtrIndex2timeDone = false;
    var intervalsDone = false;
    var sectionsDone = false;
    var indexmapDone = false;
    var numbScoreDone = false;

    $.ajax(intervalsurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            intervals = data;
            intervalsDone = true;
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});
    
    $.ajax(documentsurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            numbScore = data['derivedfiles']['score']['score']['numparts'];
            numbScoreDone = true;
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});

    $.ajax(indexmapurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            indexmap = data;
            indexmapDone = true;
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});

    $.ajax(notesalignurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            var elems = data.notes; 
            symbtrIndex2time = {};
            pitchintervals = [];
            for (var i=0; i<elems.length;i++){
                if (!(elems[i].IndexInScore in symbtrIndex2time)){
                    symbtrIndex2time[elems[i].IndexInScore] = [];
                }
                symbtrIndex2time[elems[i].IndexInScore].push({'start': parseFloat(elems[i].Interval[0]), 'end': parseFloat(elems[i].Interval[1])});
                pitchintervals.push({'start': parseFloat(elems[i].Interval[0]), 'end': parseFloat(elems[i].Interval[1])});
            }
            symbtrIndex2timeDone = true;
            pitchintervals.sort(function(a, b){return a['end']-b['end']});
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});

    $.ajax(sectionsurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            sections = data.links; 
            
            sectionsDone = true;
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});

    function dodraw() {
        if ( pitchDone && correctedpitchDone && symbtrIndex2timeDone && intervalsDone && sectionsDone && indexmapDone && numbScoreDone) {
            drawdata();
            
            endPeriod = 0;
            startPeriod = -1;
           
           aligns = []
            for (var i=0; i<indexmap.length;i++){
                var vals = [];
                if (indexmap[i][0] in symbtrIndex2time){
                   vals = symbtrIndex2time[indexmap[i][0]];
                }
                for (var j=0;j<vals.length;j++){
                    var color = "default";
                    for (var s = 0; s < sections.length; s++) {
                        var t0 = sections[s]['time'][0][0];
                        var t1 = sections[s]['time'][1][0];
                        if (vals[j]['start'] > t0 && vals[j]['end'] < t1){
                            color = sections[s]['name'];
                            break;
                        }
                     }
                     aligns.push({'index':indexmap[i][0], 'starttime': vals[j]['start'], 'endtime': vals[j]['end'], "color":color, "pos": indexmap[i][1], "line": indexmap[i][2]});
                }
           }
           aligns.sort(function(a, b){return a['endtime']-b['endtime']});
        }
    }
  }

function drawdata() {
    //drawwaveform();
    
    plotpitch();
    plotsmall();
    if (!scoreLoaded ){
      plotscore(1);
    }
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

    //console.log(recordinglengthseconds);
    posms = clickseconds * 1000;
    //console.log(clickseconds);
    part = Math.ceil(clickseconds / secondsPerView);
    // Update the internal position counter (counts from 0, part counts from 1)
    beginningOfView = (part - 1) * secondsPerView;
    //console.log(pagesound);
    //console.log(pagesound.duration);
    if (pagesound && pagesound.duration) {
        // We can only set a position if it's fully loaded
        var wasplaying = !pagesound.paused;
        if (wasplaying) {
            pagesound.pause();
        }
        pagesound.setPosition(posms);
        //console.log(posms);
        replacepart(part);
        //updateProgress();
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
function drawCurrentPitch(start, end){
    startPx = start % secondsPerView * 900 / secondsPerView;
    endPx = end % secondsPerView * 900 / secondsPerView;
      
    var canvas = $("#overlap-pitch")[0];
    var context = canvas.getContext("2d");
    canvas.width = 900;
    canvas.height = 256;
    context.globalAlpha = 0.5;

    context.clearRect (0, 0, 900, 900);
    context.beginPath();
    waszero = false; 
    
    for(var i=Math.floor(startPx); i< endPx; i++){
        var pos = i;
        if ( i in pitchvals){
        var tmp = pitchvals[i] ;
        if (tmp == 0 || tmp == 255) {
            waszero = true;
            context.moveTo(pos, tmp);
        } else {
            if (waszero) {
                waszero = false;
                context.moveTo(pos, tmp);
            } else {
                context.lineTo(pos, tmp);
            }
        }}
    }


    context.strokeStyle = "#DB4D4D";
    context.lineWidth = 3;
    context.stroke();
    context.strokeStyle = "#CC0000";
    context.lineWidth = 2;
    context.stroke();
    
    context.closePath();

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
    
    updateScoreProgress(currentTime);
    if (leftLargeView > 900) {
        beginningOfView = Math.floor(currentTime / secondsPerView) * secondsPerView;
        pnum = Math.floor(beginningOfView / secondsPerView + 1);
        replacepart(pnum)
    }
    timecode.html(formattime + "<span>"+recordinglengthfmt+"</span>");
    
    var futureTime = currentTime ;
    if(enabledCurrentPitch && !( lastpitch>=0 && pitchintervals[lastpitch]['start'] <= futureTime && pitchintervals[lastpitch]['end'] >= futureTime )){
        var updated = false;
        if( pitchintervals[lastpitch + 1]['start'] <=futureTime   && pitchintervals[lastpitch + 1]['end'] >= futureTime ){
            drawCurrentPitch(pitchintervals[lastpitch + 1]['start'], pitchintervals[lastpitch + 1]['end'])
            
            lastpitch = lastpitch+1;
            updated = true;
        
        }
        if(!updated){
            for (var i=0; i<pitchintervals.length; i++){
                if (pitchintervals[i]['start'] < futureTime && pitchintervals[i]['end'] > futureTime){
                    drawCurrentPitch(pitchintervals[i]['start'], pitchintervals[i]['end'])
                    lastpitch = i;
                    return;
                }
            }
        }
    }
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


