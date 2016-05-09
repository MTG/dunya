$(document).ready(function() {
     hasfinished = false;
     currentWork = null;
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
     currentSymbtrIndex = 1;
     currentInterval = 1;
     currentPage = 0;
     lastOffset = null;
     lastTime = null;
     showingNote = null;
     colors = ["#FFC400","#00FFB3","#0099FF","#FF007F","#00FFFF", "#FF000D","#FF9100","#4800FF","#00FF40","#D4D390","#404036","#00FF80","#8471BD","#C47766","#66B3C4","#1627D9","#16D9A2","#D99B16"]
     images = [];
     startLoaded = 0;
     lastLoaded = 0;
     contextNames = [];
     lastIndex = -1;
     lastpitch = -1; 
     scoreLoaded = false;
     barPages = {};
     histogramMax = 0;
     lastnote = null;
     // What point in seconds the left-hand side of the
     // image refers to.
     beginningOfView = 0;
     secondsUsedPerView = ratioUsedView * secondsPerView;
     // The 900 pitch values currently on screen
     pitchvals = new Array(900);
     histovals = new Array(900);
     audioCtx = new (window.AudioContext || window.webkitAudioContext)();
     oscillator = audioCtx.createOscillator();
     gainNode = audioCtx.createGain();
     oscillator.connect(gainNode);
     gainNode.connect(audioCtx.destination);
     oscillator.type = 'sine';
     gainNode.gain.value = 0;
     oscillator.start(0);    
     soundManager.onready(function() {
       pagesound = soundManager.createSound({
               url: audiourl,
         }).load();

     });

     $('.folButton').click(function(e){
       playNextSection(true);      
     });
     $('.revButton').click(function(e){
       playNextSection(false);      
     });

     $('.works-info').click(function(e){
        if(e.target.nodeName !="IMG"){
          $('.work-info').hide();
          $($(this).find(".work-ref").attr('ref')).show();
          return false;
        }
     });
     $('.work-ref').click(function(e){
        $('.work-info').hide();
        $($(this).attr('ref')).show();
        return false;
     });    
     waveform.click(function(e) {
		var offset_l = $(this).offset().left - $(window).scrollLeft();
		var left = Math.round( (e.clientX - offset_l) );
	    mouPlay(left);
     });
     waveform.mouseenter(function(e) {
             waveform.css("cursor", "pointer");
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

     loaddata();

});

function plothistogram() {
    var histogram = $("#histogramcanvas")[0];
    histogram.width = 200;
    histogram.height = 256;
    var context = histogram.getContext("2d");
    histogramMax = 0;
    var data = histogramdata;
    for (var i = 0; i < data['vals'].length; i++) {
        if (data['vals'][i] > histogramMax) {
            histogramMax = data['vals'][i];
        }
    }
    
    var lastStables = [];
    for (key in notemodels[currentWork]){
        var currMax = 0;
        for (var i = 0; i < notemodels[currentWork][key]['distribution']['vals'].length; i++) {
            if (notemodels[currentWork][key]['distribution']['vals'][i] > histogramMax) {
                histogramMax = notemodels[currentWork][key]['distribution']['vals'][i];
            }
        }
        lastStables.push([notemodels[currentWork][key]['stablepitch']['Value'], key, notemodels[currentWork][key]['interval']['Value']]);
    }
    plotRefFreq(context, lastStables); 
    plothistogrampart(context, data);
}
/*
 * Sets the event for showing the frequency at the mouse position, 
 * also draws tonic on canvas
 */
function plotRefFreq(context, lastStables){
  var positiveFreqs = lastStables.filter(function (el) {
        return el[2] >= 0;
    });
    lastStables = positiveFreqs;
    lastStables.sort(function(a, b){return a[2]-b[2]}); 

    histogramcanvas = $('.waveLabel canvas');
    histogramcanvas.mousemove(function(e) {
        var sectionName = ''; 
        var rect = histogramcanvas[0].getBoundingClientRect();
        var mousePos = e.clientY - rect.top;
        if (lastStables) {
            var offset_t = $(this).offset().top - $(window).scrollTop();
            var vtop = Math.round( (e.clientY - offset_t) );
            var freq = ( (parseInt(pitchMax) - parseInt(pitchMin)) * (255-parseInt(vtop)))/255 + parseInt(pitchMin);
            var note = null;
            var cents = null;
            for (var i=0; i<lastStables.length; i++){
                  var cent = 1200*Math.log2(freq/lastStables[i][0])
                  if( Math.abs(cent) < 50 ){
                  note = lastStables[i][1];
                  cents = Math.floor(lastStables[i][2]);
                  break;
                }
            }
            var html = "";
            if (note != null){
              html += "<b>" + note + "</b>, ";
            }
            if(cents){
              html += Math.floor(lastStables[i][0]) + " Hz";
              html += ", " + Math.floor(lastStables[i][2]) +" cents";
            }else{
              html += Math.floor(freq) + " Hz";
            }
            $("#freq-info").html(html);
            $("#freq-info").show();
            $("#freq-info").css({
                "top" : e.pageY - $(this).offset().top,
                "left" : e.pageX - $(this).offset().left + 15 
            });
        }
     });
     histogramcanvas.click(function(e) {
        var sectionName = ''; 
        var rect = histogramcanvas[0].getBoundingClientRect();
        var mousePos = e.clientY - rect.top;
        var offset_t = $(this).offset().top - $(window).scrollTop();
        var vtop = Math.round( (e.clientY - offset_t) );
        var freq = ( (parseInt(pitchMax) - parseInt(pitchMin)) * (255-parseInt(vtop)))/255 + parseInt(pitchMin);
        if (lastStables) {
            var fix_freq = null;
            for (var i=0; i<lastStables.length; i++){
                  var cent = 1200*Math.log2(freq/lastStables[i][0])
                  if( Math.abs(cent) < 50 ){
                  fix_freq = Math.floor(lastStables[i][0]);
                  break;
                }
            }
            if(fix_freq){
              play_osc(Math.floor(lastStables[i][0])); 
            }else{
              play_osc(Math.floor(freq)); 
            }
        }
     });
     
     histogramcanvas.mouseleave(function() {
        $("#freq-info").hide();
     });

    for (var i=0; i<lastStables.length; i++){
      if(lastStables[i][2]==0 ) {
         var freq = Math.floor(lastStables[i][0]);
         var j = (freq - pitchMin) / ( pitchMax - pitchMin );
         context.font = "Bold 12px Open Sans";
         context.fillText(lastStables[i][1]+": ", 120 ,265-Math.round(j*255));
         context.font = "12px Open Sans";
         context.fillText(freq + " Hz", 150 ,265-Math.round(j*255));
         context.beginPath();
         context.moveTo(0, 255-Math.round(j*255));
         for (k=0;k<130;k+=10){
             context.lineTo(k, 255-Math.round(j*255));
             context.moveTo(k+5, 255-Math.round(j*255));
         }
      }
      context.lineWidth = 1;
      context.strokeStyle = "#000";
      context.stroke();
      context.closePath();
    }
}
/*
 * Given data and color, plots histogram of frequencies. Used por current note and whole histogram.
 */
function plothistogrampart(context, data, color){
    context.beginPath();
    var lastv = [];
    var lastj = 0;
    for (var i = 0; i < data['vals'].length; i++) {
        var v = (data['vals'][i]) * 200/histogramMax;
        var j = (data['bins'][i] - pitchMin) / ( pitchMax - pitchMin );
        curr = 255-Math.round(j*255);
        lastv.push(v);
        if (curr != lastj){
            sum = 0;
            for (var r=0;r<lastv.length;r++){
                sum+=lastv[r];
            }
            context.lineTo(sum/lastv.length, curr);
            lastv = [];
        }
        lastj = curr;
        
    }
    context.lineWidth = 2;
    if(color){
        context.strokeStyle = color;
    }else{
        context.strokeStyle = "#e71d25";
    }
    context.stroke();
    context.closePath();

}
function plottonic(context) {
    // Sa and sa+1 line.
    context.beginPath();
    // sa+1, dotted
    var tonic = Math.floor(tonicdata[currentWork]['scoreInformed']['Value']);
    var tonicval = 255-(255 *(tonic - pitchMin) / (pitchMax - pitchMin));
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
    var skip = secondsPerView / 4 ;
    // Start is in samples
    var start = beginningOfView * 900 * skip / secondsPerView;
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
    $('.highlight').removeClass('highlight');
    $('#syllable-'+index).addClass('highlight');
}
function disableScore(currentTime){
    if (currentTime > (endPeriod+1) || currentTime < (startPeriod-1)){
        $('.highlight').removeClass('highlight');
        $("#no-score").show(); 
        $("#score-cont").hide(); 
    }
}
function showNoteOnHistogram(note, time){
   if (!note ){
       showingNote = null;
       $('#current-note').hide();
       return;
   }
   var histogram = $("#histogram-current-note")[0]; 
   var ctxNotes = histogram.getContext("2d");

   var currPos = (time % 8);
   currPos = (time -beginningOfView) * 900 / secondsPerView ;
   var pitch = histovals[Math.floor(currPos)];
   if (!pitch){
       ctxNotes.clearRect(0, 0, 900, 900);
       return ;
   }


   $('#current-note').show();

   if (showingNote!=note){
       histogram.width = 200;
       histogram.height = 256;
       var ctxNotes = histogram.getContext("2d");
       plothistogrampart(ctxNotes, notemodels[currentWork][note]['distribution'], "#0099FF");
       $('#current-note').html("Current Note:<br /><b>" + note + "</b>");
       showingNote=note;
   }
}
function updateFrequencyMarker(time){
   var canvas = $('#overlap-histogram')[0];
   canvas.width = 200;
   canvas.height = 256;
   var context = canvas.getContext("2d");
   if (time % 2){
     var currPos = (time % 8);
        
     currPos = (time -beginningOfView) * 900 / secondsPerView ;
     var pitch = histovals[Math.floor(currPos)];
     if (!pitch){
         var pitch = pitchvals[Math.floor(currPos)];
     }
     
     if (!pitch || pitch>250){
         context.clearRect(0, 0, 900, 900);
         return ;
     }
     
     var curr = pitch;
     context.beginPath(); 
     context.moveTo(0, curr); 
     context.lineTo(200, curr); 
     context.lineWidth = 1; 
     context.strokeStyle = 'rgba(0,0,0,0.9)';
     context.fillStyle = 'rgba(0,0,0,0.9)';
     context.stroke(); 
     context.closePath();
   }  
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
                plotscore(aligns[lastIndex]['index'])   
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
                    plotscore(aligns[i]['index'], color); 
                    lastIndex = i;
                    return;
                }
            }
        }
        disableScore(currentTime); 
    }
}

function plotpitch(pnum) {
    // In order to account for slow internet connections,
    // we always load one image ahead of what we need.
    // TODO: We need to know when the final image is.
    var extraImg = null;
    var div = Math.floor(pnum/2);
    if (pnum % 2 == 0){
        var extraImg = getImage(div);
    }
    var spec = getImage(div + 1);
    var view = new Uint8Array(pitchdata);
    var canvas = $("#pitchcanvas")[0];
    canvas.width = 900;
    canvas.height = 256;
    var context = canvas.getContext("2d");
    loading = true;
    var changeImage = function() {
      if (spec.complete && (extraImg == null || extraImg.complete)){
            if (extraImg != null){
                var imageSize = ratioUsedView * 900;
                context.drawImage(spec, 0, 0, imageSize, 256, imageSize, 0, imageSize, 256);
                context.drawImage(extraImg, imageSize, 0, imageSize, 256, 0, 0, imageSize, 256);
            }else{
                context.drawImage(spec, 0, 0);
            }
            spectrogram(context, view, ["#8A8A8A", "#FFFFFF"]);
            loading = false;
        }
    }
    
    if (spec.complete){
        changeImage();
    }
    spec.onload = changeImage;
    if (extraImg!=null){
        extraImg.onload = changeImage;
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
            context.globalAlpha = 0.2;
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
        context.drawImage(small, 0, 0, small.width, small.height, 0, 0, 900, 64);
        //smallFill(banshidata, banshicolours);
        //smallFill(luogudata, "#0f0");
    
        // Draw sections on smallcanvas
        var sec = [];
        for (w in sections){
            sec = sec.concat(sections[w]['links'])
        }
        colorsNames = {};
        currColor = 0;
        for (var i = 0; i < sec.length; i++) {
                var name = sec[i]['name'];
                if (!(name in colorsNames)){
                    colorsNames[name]=colors[currColor];
                    currColor += 1;
                }
        }
        smallFill(sec, "#0ff", colorsNames);
    }
}

function sortNumber(a,b) {
    return a - b;
}
function loaddata() {

    var loadingDone= 0;
    var partsLoaded= 0;
    var indexLoaded= 0;
    var partsDone = false;
    var indexmapDone = false;
    var notemodelsLoaded = false;
    var histogramLoaded = false;
    $.ajax(worksurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            numbScore = {};
            phrase = {};
            indexmap = {};
            worksdata = data;
            minInterval = 9999;
            for (w in worksdata){
              if(Object.keys(worksdata).length > 1){ 
                var position = 900*(worksdata[w]["from"]/recordinglengthseconds) ;
                var width = 900*((worksdata[w]["to"]- worksdata[w]["from"])/recordinglengthseconds) ;
                $('#work-name-' + w).show();  
                $('#work-name-' + w).css("margin-left",position+"px");
                $('#work-name-' + w).css("width",width+"px");
              }
                if (minInterval > worksdata[w]["from"]){
                    minInterval = worksdata[w]["from"];
                    currentWork = w;
                }
                workDocumentsUrl = documentsurl + w;
                           
                $.ajax(workDocumentsUrl, {dataType: "json", type: "GET",
                    context: {work: w},
                    success: function(data, textStatus, xhr) {
                        numbScore[this.work] = data['derivedfiles']['score']['score']['numparts'];
                        partsLoaded++;
                        if (partsLoaded == Object.keys(worksdata).length ){  
                           partsDone = true;
                        }
                        dodraw();
                }, error: function(xhr, textStatus, errorThrown) {
                   console.debug("xhr error " + textStatus);
                   console.debug(errorThrown);
                   $('#dialog').html('This recording is not analyzed yet.')
                }});
                $.ajax(workDocumentsUrl + indexmapurl, {dataType: "json", type: "GET",
                    context: {work: w},
                    success: function(data, textStatus, xhr) {
                        indexmap[this.work] = data;
                        indexLoaded++;
                        if (indexLoaded == Object.keys(worksdata).length){  
                            indexmapDone = true;
                        }
                        dodraw();
                }, error: function(xhr, textStatus, errorThrown) {
                   console.debug("xhr error " + textStatus);
                   console.debug(errorThrown);
                   $('#dialog').html('This recording is not analyzed yet.')
                }});

                $.ajax(workDocumentsUrl + phraseurl, {dataType: "json", type: "GET",
                    context: {work: w},
                    success: function(data, textStatus, xhr) {
                        phrase[this.work] = data[0]["boundary_noteIdx"];
                }, error: function(xhr, textStatus, errorThrown) {
                   console.debug("xhr error " + textStatus);
                   console.debug(errorThrown);
                }});
            }
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }}); 


    // We do pitch track with manual httprequest, because
    // we want typedarray access

    var oReq = new XMLHttpRequest();
    oReq.open("GET", pitchtrackurl, true);
    oReq.responseType = "arraybuffer";
    oReq.onload = function(oEvent) {
        if (oReq.status == 200) {
            pitchdata = oReq.response;
            loadingDone++;
            dodraw();
        }
    };
    oReq.send();
    
    $.ajax(tonicurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            tonicdata = data;
            loadingDone++;
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});
    
    $.ajax(histogramurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            histogramdata = data;
            histogramLoaded = true;
            dodrawHistogram();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});
        
    $.ajax(notemodelsurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            notemodels = data;
            notemodelsLoaded = true;
            dodrawHistogram();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});

    $.ajax(ahenkurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
         for (w in data){
           $("#work-" + w).append("<label>Ahenk:</label><b><span>" + data[w][0] + "</span></b>") 

         }
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});
    $.ajax(notesalignurl, {dataType: "json", type: "GET",
    success: function(data, textStatus, xhr) {
        var elems = data; 
        symbtrIndex2time = {};
        pitchintervals = [];
        for (var i=0; i<elems.length;i++){
          var start = elems[i][0];
          var end = elems[i][1];
          var sid = elems[i][3];
          if(! (sid in symbtrIndex2time)){
            symbtrIndex2time[sid] = [];
          }
          symbtrIndex2time[sid].push({'start': start, 'end': end});
          pitchintervals.push({'start': start, 'end': end});
        }
        loadingDone++;
        pitchintervals.sort(function(a, b){return a['end']-b['end']});
        dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});

    $.ajax(sectionsurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            sections = data; 
            loadingDone++;
            dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});
    
    function dodrawHistogram() {
        if (histogramLoaded && notemodelsLoaded) {
            plothistogram();
        
            if (loadingDone == 4 && indexmapDone && partsDone) {
                $('#dialog').dialog('close');
            }
        }
    }
    function dodraw() {
        if (loadingDone == 4 && indexmapDone && partsDone) {
            
            endPeriod = 0;
            startPeriod = -1;
            addedNotes = {};

            aligns = []
            alignment = JSON.parse(alignment);
            for (i in alignment['alignedLyricsSyllables']){
              var elem = alignment['alignedLyricsSyllables'][i];
              var html = "<div class='lyric-line'>";
              for (j in elem){
                var subHtml = '';
                var add = false;
                for (k in elem[j]){
                  if (!(elem[j][k][3] in addedNotes)){
                    add = true;
                    addedNotes[elem[j][k][3]] = '';
                  }
                  subHtml += "<span id=syllable-"+ elem[j][k][3] +">" + elem[j][k][2]+ "</span>";
                  aligns.push({'index':elem[j][k][3], 'starttime': elem[j][k][0], 'endtime': elem[j][k][1]});
                } 
                if (add){
                  html += "<span class='lyric' >" + subHtml + "</span>"
                }
              }
              html += "</div>";
              $('#score').append(html)

            }
           aligns.sort(function(a, b){return a['index']-b['index']});
           drawdata(false);
           
           if (histogramLoaded && notemodelsLoaded) {
               $('#dialog').dialog('close');
           }
        }
    }
}

function drawdata(disablePitch) {
    
    if(disablePitch!=true){
        plotpitch(1);
    }
    plotsmall();
    if (!scoreLoaded ){
      //plotscore(1);
    }
    var start = beginningOfView;
    var skip = secondsUsedPerView/ 2;
    $(".timecode1").html(formatseconds(start));
    $(".timecode2").html(formatseconds(start+skip));
    $(".timecode3").html(formatseconds(start+skip*2));
    $(".timecode4").html(formatseconds(start+skip*3));
    $(".timecode5").html(formatseconds(start+skip*4));

    // The highlighted miniview
    var beginPercentage = (beginningOfView/recordinglengthseconds);
    var endPercentage = (beginningOfView + secondsUsedPerView) / recordinglengthseconds;

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
    if (pagesound && pagesound.duration) {
        // We can only set a position if it's fully loaded
        var wasplaying = !pagesound.paused;
        if (wasplaying) {
            pagesound.pause();
        }
        pagesound.setPosition(posms);
        updateView();
        updateProgress();
        if (wasplaying) {
            pagesound.resume();
        }
    }
}

function play() {
    if (hasfinished) {
        hasfinished = false;
        plotpitch(1);
        beginningOfView = 0;
        drawdata(false);
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

function drawCurrentPitch(start, end, note){
    startPx = (start - beginningOfView) * 900 / secondsPerView ;
    endPx = (end - beginningOfView) * 900 / secondsPerView ;
    var canvas = $("#overlap-pitch")[0];
    var context = canvas.getContext("2d");
    canvas.width = 900;
    canvas.height = 256;
    context.globalAlpha = 0.5;

    context.clearRect (0, 0, 900, 900);
    context.beginPath();
    waszero = false; 
    histovals = new Array(900);
    for(var i=Math.floor(startPx); i< endPx; i++){
        var pos = i;
        if ( i in pitchvals){
            var tmp = pitchvals[i] ;
            histovals[i] = tmp ;
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
            }
        }
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
    ampleMask = rendersMask.width();
    ampleRenders = renders.width();
    ampleRenderTotal = renderTotal.width();
    var currentTime = pagesound.position / 1000 ;
    // formatseconds appears to run 1 second ahead of time,
    // so correct for it here
    formattime = formatseconds(currentTime-1);
    // Fix currentTime because of firstView
    // use only from 25% of the view to 75%
    progress_percent = (currentTime - beginningOfView ) / secondsPerView ;
    leftLargeView = ampleRenders *progress_percent ;
    
    total_progress_frac = (currentTime/recordinglengthseconds);
    leftSmallView = ampleRenderTotal*total_progress_frac;
    
    capcal.css('left', leftLargeView-5);
    capcalTotal.css('left', leftSmallView-6);
    
    updateScoreProgress(currentTime);
    if (progress_percent >= (1-ratioUsedView/2)) {
        updateView();
    }
    timecode.html(formattime + "<span>"+recordinglengthfmt+"</span>");
    
    updateCurrentPitch();
};
function updateView(){
    var currentTime = pagesound.position / 1000 ;
    hideCurrentPitch();
    beginningOfView = Math.floor(currentTime / secondsUsedPerView ) * secondsUsedPerView ;
    pnum = Math.floor(beginningOfView / secondsUsedPerView + 1) ;
    plotpitch(pnum);
    drawdata(true);
}
function updateCurrentPitch(){
    var futureTime = pagesound.position / 1000 ;
    for (w in worksdata){
        if (futureTime < worksdata[w]["to"] && futureTime > worksdata[w]["from"]){
            currentWork = w;
            plothistogram();
            break;
        }
    }
    if(!loading && !( lastpitch>=0 && pitchintervals[lastpitch]['start'] <= futureTime && pitchintervals[lastpitch]['end'] >= futureTime )){
        var updated = false;
        if( pitchintervals[lastpitch + 1]['start'] <=futureTime   && pitchintervals[lastpitch + 1]['end'] >= futureTime ){
            drawCurrentPitch(pitchintervals[lastpitch + 1]['start'], pitchintervals[lastpitch + 1]['end'], pitchintervals[lastpitch + 1]['note'])
            lastnote = pitchintervals[lastpitch + 1]['note'];
            lastpitch = lastpitch+1;
            updated = true;
            lastTime = futureTime;
        }
        if(!updated){
            for (var i=0; i<pitchintervals.length; i++){
                if (pitchintervals[i]['start'] < futureTime && pitchintervals[i]['end'] > futureTime){
                    drawCurrentPitch(pitchintervals[i]['start'], pitchintervals[i]['end'], pitchintervals[i]['note'])
                    lastnote = pitchintervals[lastpitch + 1]['note'];
                    lastpitch = i;
            lastTime = futureTime;
                    return;
                }
            }
        }
    }else if(lastTime+1 < futureTime ){
        // If no update since last second then hide current pitch
        hideCurrentPitch();
    }
    showNoteOnHistogram(lastnote, futureTime);
    updateFrequencyMarker(futureTime);
}

function play_osc(f){
    gainNode.gain.cancelScheduledValues(audioCtx.currentTime);
    var waveArray = new Float32Array(9);
    waveArray[0] = 0.00001;
    waveArray[1] = 0.5;
    waveArray[2] = 0.5;
    waveArray[3] = 0.5;
    waveArray[4] = 0.5;
    waveArray[5] = 0.5;
    waveArray[6] = 0.5;
    waveArray[7] = 0.5;
    waveArray[8] = 0.5;
    oscillator.frequency.value = f; // value in hertz
    gainNode.gain.setValueCurveAtTime(waveArray, audioCtx.currentTime, 0.5);
    window.setTimeout(function(){
      try {
        //ExponentialRamp can't handle 0 so we pass 0.00001
        gainNode.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 2);
      }
      catch (e) {
        console.log(e);
      }
    }, 1000);
}
function playNextSection(right){
  var changepos = null;
  var starts= []
  var ends = []
  var currentTime=pagesound.position / 1000 ;
  for (w in sections){
    for (var s = 0; s < sections[w]['links'].length; s++) {
       starts.push(parseFloat(sections[w]['links'][s]['time'][0][0]));
        ends.push(parseFloat(sections[w]['links'][s]['time'][1][0]));
    }  
  }
  starts.sort(function(a, b){ return a - b;});
  ends.sort(function(a, b){ return a - b;});
  if (right && (currentTime <= starts[0] || currentTime >= starts[starts.length-1])){
     changepos = starts[0]+0.1;
  }else if (!right && (currentTime < ends[0] || currentTime > ends[ends.length-1])){
      changepos = starts[starts.length-1]+0.1;
  }
  if(changepos == null){
    for(var s = 0; s < starts.length;s++){
        if(starts[s]<=currentTime && ends[s]>=currentTime){
          if(right){  
            changepos = starts[s+1]+0.1;
          }else{
            changepos = starts[s-1]+0.1;
          }
          break;
        }
    }
  }
  if(changepos != null){
      beginningOfView = Math.floor((changepos / secondsUsedPerView ) - 1) * secondsUsedPerView ;
      pnum = Math.floor(beginningOfView / secondsUsedPerView + 1) ;
      pagesound.setPosition(changepos * 1000);
      plotpitch(pnum);
      //updateView();
  }
  updateProgress();
}
function hideCurrentPitch(){
  $("#current-note").hide();
  var canvas = $("#overlap-pitch")[0];
  var context = canvas.getContext("2d");
  context.clearRect (0, 0, 900, 900);
  histovals = new Array(900);
}
function getImage(part){
    if (lastLoaded > part && startLoaded < part){
      return images[part-startLoaded]
    }
    startLoaded = part;
    pnumMax = Math.floor(recordinglengthseconds / secondsUsedPerView + 1) ;
    for(var i=part; i<pnumMax && (i-startLoaded)<10 ;i++){
        var spec = new Image();
        spec.src = specurl.replace(/part=[0-9]+/, "part="+i);
        images[i -startLoaded]=spec;
        lastLoaded=i;
    }
    return images[part- startLoaded]
} 
