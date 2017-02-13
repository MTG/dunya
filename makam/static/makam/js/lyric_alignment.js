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
function updateScoreProgress(currentTime){
    if (currentTime > endPeriod || currentTime < startPeriod)
    {
        var updated = false;
        if (lastIndex && aligns.length < (lastIndex + 1)){
            aligns[lastIndex+1]['starttime'];
            if (aligns[lastIndex+1]['starttime']<currentTime && aligns[lastIndex+1]['endtime']>currentTime){
                endPeriod = aligns[lastIndex+1]['endtime'];
                startPeriod = aligns[lastIndex+1]['starttime'];           
                plotscore(aligns[i]['index'])   
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
          sec = sec.concat(sections[w])
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
    $.ajax(worksurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
            numbScore = {};
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
    
    $.ajax(ahenkurl, {dataType: "json", type: "GET",
        success: function(data, textStatus, xhr) {
         for (w in data){
           $("#work-" + w).append("<label>Ahenk:</label><b><span>" + data[w]['name'] + "</span></b>") 

         }
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
    }});
    $.ajax(notesalignurl, {dataType: "json", type: "GET",
    success: function(data, textStatus, xhr) {
        var elems = data;
        alignment = data;
        symbtrIndex2time = {};
        loadingDone++;
        dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});
    $.ajax(alignsectionsurl, {dataType: "json", type: "GET",
    success: function(data, textStatus, xhr) {
        sections = data;
        loadingDone++;
        dodraw();
    }, error: function(xhr, textStatus, errorThrown) {
       console.debug("xhr error " + textStatus);
       console.debug(errorThrown);
       $('#dialog').html('This recording is not analyzed yet.')
    }});
    function dodraw() {
        if (loadingDone == 4 && indexmapDone && partsDone) {
            if (alignment.length == 0) {
              $('#score').html('<div id="no-score">There is no score to show.</div>');
            } 
            endPeriod = 0;
            startPeriod = -1;
            addedNotes = {};

            aligns = []
            for (i in alignment){
              var elem = alignment[i];
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
            break;
        }
    }
}

function playNextSection(right){
  var changepos = null;
  var starts= []
  var ends = []
  var currentTime=pagesound.position / 1000 ;
  for (w in sections){
    for (var s = 0; s < sections[w].length; s++) {
       starts.push(parseFloat(sections[w][s]['time'][0]));
        ends.push(parseFloat(sections[w][s]['time'][1]));
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
