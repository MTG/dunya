var filtersArray = new Array();
var filtersOutputArray = new Object();
var filtersLiteralOutputArray = new Object();

function removeFilter(entity_filter){
	$(".filterBall").parent().find(".formFilter").addClass("formFilterClosed");
	$(".filterBall").parent().find(".filterGlobalList").addClass("filterListClosed");
	$(".filterBall").find(".arrow").addClass("arrowClosed");
	$(".filterBall").addClass("filterBallClosed");
	$("#entitiesList").addClass("filterListClosed");
	$(".filters.entity_"+entity_filter).remove();
	filtersArray.splice(filtersArray.indexOf(entity_filter), 1);
}

function loadFilter(entity_filter,eid){

	$(".filterBall").parent().find(".formFilter").addClass("formFilterClosed");
	$(".filterBall").parent().find(".filterGlobalList").addClass("filterListClosed");
	$(".filterBall").find(".arrow").addClass("arrowClosed");
	$(".filterBall").addClass("filterBallClosed");
	$("#entitiesList").addClass("filterListClosed");

	if(entity_filter==1){
		filterFile = "/static/carnatic/js/carnatic_artists.json";
		filterName = "Artist";
	}else if(entity_filter==2){
		filterFile = "/static/carnatic/js/carnatic_concerts.json";
		filterName = "Concert";
	}else if(entity_filter==3){
		filterFile = "/static/carnatic/js/carnatic_works.json";
		filterName = "Work";
	}else if(entity_filter==4){
		filterFile = "/static/carnatic/js/carnatic_artists.json";
		filterName = "Instrument";
	}else if(entity_filter==5){
	 	filterFile = "/static/carnatic/js/carnatic_artists.json";
	 	filterName = "Raaga";
	}else if(entity_filter==6){
		filterFile = "/static/carnatic/js/carnatic_recordings.json";
		filterName = "Taala";
	}
	getFilterData(filterFile,entity_filter,filterName,eid);
}

function getFilterData(filterFile,entity_filter,filterName,eid){
	window.filterData = "";
    $.ajax({
    	url: filterFile,
		data: "nocache=" + Math.random(),
		type: "GET",
		dataType: "json",
		success: function(source){
			window.filterData = source;
			showFilterData(entity_filter,filterName,eid);
		},
		error: function(dato){
			alert("ERROR while loading JSON");
		}
	});
}

function parseAllFilters(){
    $.each(window.filtersItems, function(index, element) {
    	entityHTML = "<li class='entity_"+(index+1)+"' entity_id='"+(index+1)+"' eid='eid"+(index+1)+"'><div class='colorCode shadow1'></div>"+element.name+"</li>";
    	$("#entitiesList ul").append(entityHTML);
    	formHTML = "<div class='form_"+(index+1)+"'><form>";
    	$.each(element.data, function(index2, element2) {
    		formType = element2.type;
    		if(formType=="list"){
    			if (element2.multiselect) {
                    var filtertype = 'multiSelect';
                } else {
                    var filtertype = 'select';
                }
                formHTML += "<fieldset filtertype='"+filtertype+"' filtername='"+element2.name+"'>";
                formHTML += "<label class='formSection'>"+element2.name+"</label>";
                formHTML += "<div class='filterList formFilterItem'><ul>";
                for( i in element2.data ){
                    formHTML += "<li the_id='"+(parseInt(i)+1)+"' valor='"+element2.data[i]+"'>"+element2.data[i]+"</li>";
                }
                formHTML += "</ul></div></fieldset>";
    		}else if(formType=="rangeslider"){
	    		formHTML += "<fieldset filtertype='slideRange' filtername='"+element2.name+"'>";
		        formHTML += "<label class='formSection'>"+element2.name+"</label>";
		        formHTML += "<div class='formFilterItem'>";
			    formHTML += "<span class='output'></span>";
			    if(element2.step){
				    formHTML += "<div class='slider-range' min='"+element2.data[0]+"' max='"+element2.data[1]+"' step='"+element2.step+"'></div>";
			    }else{
			    	formHTML += "<div class='slider-range' min='"+element2.data[0]+"' max='"+element2.data[1]+"' ></div>";
			    }
		        formHTML += "</div></fieldset>";
    		}else if(formType=="text"){
	    		formHTML += "<fieldset filtertype='text' filtername='"+element2.name+"'>";
		        formHTML += "<label class='formSectionText'>"+element2.name+"<input type='text' /></label>";
		        formHTML += "</fieldset>";
    		}
    	});
	    formHTML += "</form></div>";
	    $("#footage").append(formHTML);
    });
    loadClicks();
}

function loadClicks(){

	/* Select Music Style */
	$("#gmSelected").click(function(){
		$("#gmDropDown").show();
	});

	$("#entitiesList ul li").click(function(){
		if($(this).hasClass("selected")){
			removeFilter($(this).attr("entity_id"));
		}else{
			loadFilter($(this).attr("entity_id"),$(this).attr("eid"));
		}
		$(this).toggleClass("selected");
		$("#summary").attr("class","entity_"+$(this).attr("entity_id"));
	});

	$(".filterList.formFilterItem ul li").click(function(){
		$(this).toggleClass("selected");
		entity = $(this).parent().parent().parent().parent().parent().parent().parent().attr("eid");
		filterType = $(this).parent().parent().parent().attr("filtertype");
		filterName = $(this).parent().parent().parent().attr("filtername");
		getResults($(this));
	});


	$(".formSection").click(function(){
		$(this).toggleClass("formSectionOpen");
		$(this).nextAll(".formFilterItem").toggle();
		$(".formSection").not(this).removeClass("formSectionOpen");
		$(".formSection").not(this).nextAll(".formFilterItem").hide();
		topPosition = $(this).position()
		container = $(this).parent().parent().parent().parent();
		container.scrollTop(topPosition.top-10);
		if($(this).hasClass("formSectionOpen")){
			container.addClass("noScroll");
		}else{
			container.removeClass("noScroll");
		}
	});
	$(".filterBall").click(function(){
		nuk = $(this);
		if($(this).hasClass("filterBallClosed")){
			$(".filterBall").not(this).parent().find(".formFilter").addClass("formFilterClosed");
			$(".filterBall").not(this).parent().find(".filterGlobalList").addClass("filterListClosed");
			$("#entitiesList").addClass("filterListClosed");
			$(".filterBall").not(this).find(".arrow").addClass("arrowClosed");
			$(".filterBall").not(this).addClass("filterBallClosed");
			nuk.find(".arrow").removeClass("arrowClosed");
			nuk.removeClass("filterBallClosed");
			nuk.siblings(".formFilter").removeClass("formFilterClosed");
			nuk.siblings(".filterGlobalList").removeClass("filterListClosed");
			nuk.siblings("#entitiesList").removeClass("filterListClosed");
			sumarizeFilter($(this));
		}else{
			$(".filterBall").parent().find(".formFilter").addClass("formFilterClosed");
			$(".filterBall").parent().find(".filterGlobalList").addClass("filterListClosed");
			$(".filterBall").find(".arrow").addClass("arrowClosed");
			$(".filterBall").addClass("filterBallClosed");
			$("#entitiesList").addClass("filterListClosed");
			sumarizeFilter($(this));
		}
	});

	$("#toggleMain").click(function(){
		$("#filterMask").toggleClass('querybar');
	});
}

function sumarizeFilter(object){

	summaryHTML = "";
	$.each(filtersLiteralOutputArray[object.parent().attr("eid")], function(nom, valors) {
		summaryHTML += "<b>" + nom +"</b>" + valors+"</br>";
    });
	object.find(".filterSummary").html(summaryHTML);

}

function showFilterData(entity_filter,filterName,eid){
	filtersArray.push(entity_filter);
	filterPosition = filtersArray.indexOf(entity_filter);
	$('#filterModel').clone(true).appendTo("#filterArea").attr("id","filter_"+filterPosition).attr("class","filters entity_"+entity_filter).attr("eid",eid);
	entityHTML_bc = "<div class='bread entity_"+entity_filter+"'><div class='breadarrow'></div><span><a href='#'>No selection</a></span></div>";
	$("#breadcrumb").append(entityHTML_bc);
	$('#filterArea').width(480+(filtersArray.length*780));
	newFilter = "#filter_"+filterPosition;
    $(newFilter).find(".filterList").append(listFilterData(entity_filter));
    $(newFilter).find(".filterList ul li").click(function(){
  		$(this).toggleClass("selected");
  		$("#breadcrumb").find(".entity_"+entity_filter+" span a").html($(this).html());
	});
    $(newFilter).find(".filterBall span").html(filterName);
    //$(newFilter).find(".formFilter").html($(".form_"+entity_filter).html());
    $(".form_"+entity_filter).clone(true).appendTo($(newFilter).find(".formFilter"));
    //$(newFilter).find(".formFilter").html($(".form_"+entity_filter).html());

    $(newFilter+" .formFilter").removeClass("formFilterClosed");
	$(newFilter+" .filterList").removeClass("filterListClosed");
	$(newFilter+" .filterBall .arrow").removeClass("arrowClosed");
	$(newFilter+" .filterBall").removeClass("filterBallClosed");

    $(newFilter+" .slider-range").each(function(){
    	if($(this).attr('step')){
	    	$(this).slider({
			range: true,
			min: parseInt($(this).attr('min')),
			max: parseInt($(this).attr('max')),
			step: parseInt($(this).attr('step')),
			values: [ parseInt($(this).attr('min')), parseInt($(this).attr('max')) ],
			slide: function( event, ui ) {
				$(newFilter).find(".output").html( ui.values[ 0 ] + " - " + ui.values[ 1 ] + "<div class='results' first='"+ui.values[ 0 ]+"' second='"+ui.values[ 1 ]+"'></div>" );
			}
		});
    	}else{
	    	$(this).slider({
			range: true,
			min: parseInt($(this).attr('min')),
			max: parseInt($(this).attr('max')),
			values: [ parseInt($(this).attr('min')), parseInt($(this).attr('max')) ],
			slide: function( event, ui ) {
				$(newFilter).find(".output").html( ui.values[ 0 ] + " - " + ui.values[ 1 ] + "<div class='results' first='"+ui.values[ 0 ]+"' second='"+ui.values[ 1 ]+"'></div>" );
			}
		});
    	}

    });


    //$(newFilter).find(".output").html( $(this).parent().find(".slider-range").attr("min")+"- 2013" );
    $(newFilter).find(".output").each(function(){
    	$(this).html($(this).siblings().attr("min")+" - "+$(this).siblings().attr("max"));
    });
	$(newFilter).find("input").bind("slider:ready slider:changed", function (event, data) {
		if($(this).hasClass("artistGeneration")){
			result = 1912+(data.value.toFixed(2)*100);
  			$(this).parent().find(".output").html(result.toFixed());
		}else{
			result = data.value.toFixed(2)*100;
  			$(this).parent().find(".output").html(result.toFixed());
  			console.log("change");
		}
	});
}

function listFilterData(entity_filter){
    list = "<ul>";
    $.each(window.filterData, function(index, element) {
    	if(entity_filter==2||entity_filter==3||entity_filter==6){ list += "<li>"+element.info.title+"</li>"}
    	else{ list += "<li>"+element.info.name+"</li>"};
    });
    list += "</ul>";
    return list;
}

function getResults(item){
		theValue = "";
		theName = "";
		if( filterType == "multiSelect" ){
			theValue =[ ];
			theName =[ ];
			item.parent().find(".selected").each(function (i){
        		theValue[i]=$(this).attr("the_id");
        		theName[i]=$(this).attr("valor");
        		console.log(theName[i]);
        	});
		}else if( filterType == "select" ){
			theValue = item.parent().find(".selected").attr("the_id");
			theName = item.parent().find(".selected").attr("valor");
		}else if( filterType == "slider" ){
			theValue = "es un slider";
		}else if( filterType == "sliderRange" ){
			theValue = "es un sliderrange";
		}

		if(jQuery.isEmptyObject(filtersOutputArray)){
			filtersOutputArray[entity] = new Object();
			filtersOutputArray[entity][filterName] = theValue;
			filtersLiteralOutputArray[entity] = new Object();
			filtersLiteralOutputArray[entity][filterName] = theName;
		}else{
			for(var i in filtersOutputArray){
				if (filtersOutputArray.hasOwnProperty(entity)) {
					filtersOutputArray[entity][filterName] = theValue;
					filtersLiteralOutputArray[entity][filterName] = theName;
				}else{
					filtersOutputArray[entity] = new Object();
					filtersOutputArray[entity][filterName] = theValue;
					filtersLiteralOutputArray[entity] = new Object();
					filtersLiteralOutputArray[entity][filterName] = theName;
				}
			}
		}
	}
