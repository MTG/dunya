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


});

function plotscore(index, color) {
        
    $("#no-score").hide(); 
    $("#score-cont").show(); 
    if (!scoreLoaded ){
      for (w in worksdata){
        $("#score-cont").append('<div id="score-'+w+'"></div>');
        for(var i=1; i<=numbScore[w];i++){
            $("#score-"+w).append('<div class="score-page" id="score-'+w+'-'+i+'"></div>');
        }    
        for(var i=1; i<=numbScore[w];i++){
            score = documentsurl + w + scoreurl.replace(/part=[0-9]+/, "part="+i);
            $.ajax(score, {dataType: "text", type: "GET", 
                context: {work: w, score:i},
                success: function(data, textStatus, xhr) {
                  
                  data = data.replace('</svg>','<rect class="marker" x="0" y="0" width="0" height="0" ry="0.0000" style="fill:blue;fill-opacity:0.1;stroke-opacity:0.9" /></svg>');
                  
                  $("#score-"+this.work+"-"+this.score).append(data);
                  var bars = []
                  $("#score-"+this.work+"-"+this.score).find("rect[width='0.1900'][y='-2.0000'][height='4.0000']").each(function(){
                      var pos = $(this).attr('transform').split("(");
                      var xy = pos[1].split(", ");
                      bars.push([parseInt(xy[0]), parseInt(xy[1]), $(this)]);
                  });
                  if (! (this.work in barPages)){
                      barPages[this.work] = {};
                  }
                  barPages[this.work][this.score] = bars;
   
                 $('svg').each(function () { 
                   
                   $(this)[0].setAttribute('width', '230mm') ; 
                   $(this)[0].setAttribute('height', '139mm') ; 
                   $(this)[0].setAttribute('viewBox', '0 0 115 65') 
                 }); 
                if(document.URL.indexOf("show-phrase")>=0){     
                 
                 for (var p in phrase[this.work]){
                   for(var j=0; j<aligns.length;j++){
                       if (aligns[j]['index'] == phrase[this.work][p][0]){
                         highlightPhraseSegm(this.work, j);
                         break;
                       }
                   }
                }
                }
            }, error: function(xhr, textStatus, errorThrown) {
               console.debug("xhr error " + textStatus);
               console.debug(errorThrown);
            }});
        }
        
      }
      scoreLoaded = true;
    }else{
      if (aligns[index]){
          var find = false;
          var curr = $("#score-"+currentWork).find("a[id^=l" + aligns[index]['line'] + "-f]");
          curr.each(function(){
    
            highlightNote($(this), index);
          });
        }
    }
}

function disableScore(currentTime){
    if (currentTime > (endPeriod+1) || currentTime < (startPeriod-1)){
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
    
    timecode.html(formattime + "<span>"+recordinglengthfmt+"</span>");
    
};

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
