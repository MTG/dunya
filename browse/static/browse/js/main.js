var filtersArray = new Array();
var filtersOutputArray = new Object();
var filtersLiteralOutputArray = new Object();

function removeFilter(entity_filter){
	$(".filterBall").parent().find(".formFilter").addClass("formFilterClosed");
	$(".filterBall").parent().find(".filterGlobalList").addClass("filterListClosed");
	$(".filterBall").find(".arrow").addClass("arrowClosed");
	$(".filterBall").addClass("filterBallClosed");
	$("#entitiesList").addClass("filterListClosed");
	$(".entity_"+entity_filter).remove();
	filtersArray.splice(filtersArray.indexOf(entity_filter), 1);
}

function loadFilter(filterdata, entity_filter,eid){
	$(".filterBall").parent().find(".formFilter").addClass("formFilterClosed");
	$(".filterBall").parent().find(".filterGlobalList").addClass("filterListClosed");
	$(".filterBall").find(".arrow").addClass("arrowClosed");
	$(".filterBall").addClass("filterBallClosed");
	$("#entitiesList").addClass("filterListClosed");

	getFilterData(filterdata.url,entity_filter,filterdata.name,eid);
}

function getFilterData(filterFile,entity_filter,filterName,eid){
    $.ajax({
    	url: filterFile,
		type: "GET",
		dataType: "json",
		success: function(source){
			showFilterData(source, entity_filter,filterName,eid);
		},
		error: function(dato){
			alert("ERROR while loading JSON");
		}
	});
}

var makeFormElementList = function(element) {
    formHTML = "";
    if (element.multiselect) {
        var filtertype = 'multiSelect';
    } else {
        var filtertype = 'select';
    }
    formHTML += "<fieldset filtertype='"+filtertype+"' filtername='"+element.name+"'>";
    formHTML += "<label class='formSection'>"+element.name+"</label>";
    formHTML += "<div class='filterList formFilterItem'><ul>";
    for( i in element.data ){
        formHTML += "<li the_id='"+(parseInt(i)+1)+"' valor='"+element.data[i]+"'>"+element.data[i]+"</li>";
    }
    formHTML += "</ul></div></fieldset>";
    return formHTML;
};

var makeFormElementSlider = function(element) {
    formHTML = "";
    formHTML += "<fieldset filtertype='slideRange' filtername='"+element.name+"'>";
    formHTML += "<label class='formSection'>"+element.name+"</label>";
    formHTML += "<div class='formFilterItem'>";
    formHTML += "<span class='output'></span>";
    if(element.step){
        step = "step='"+element.step+"'";
    }
    formHTML += "<div class='slider-range' min='"+element.data[0]+"' max='"+element.data[1]+"' "+step+"></div>";
    formHTML += "</div></fieldset>";
    return formHTML;
};

var makeFormElementText = function(element) {
    formHTML = "";
    formHTML += "<fieldset filtertype='text' filtername='"+element.name+"'>";
    formHTML += "<label class='formSectionText'>"+element.name+"<input type='text' /></label>";
    formHTML += "</fieldset>";
    return formHTML;
};

function parseAllFilters(filtersItems){
    $.each(filtersItems, function(index, element) {
        console.log(element)
        entity = $("<li>", {
            entity_id: (index+1),
            eid: "eid"+(index+1)
        }).append($("<div>", {"class": "colorCode shadow1"}))
          .append(element.name);
        entity.data("filter", element);

	    $("#entitiesList ul").append(entity);
    	formHTML = "<div class='form_"+(index+1)+"'><form>";
    	formHTML += element.name;
    	$.each(element.data, function(index2, element2) {
    		formType = element2.type;
    		if(formType=="list"){
                formHTML += makeFormElementList(element2);
    		}else if(formType=="rangeslider"){
                formHTML += makeFormElementSlider(element2);
    		}else if(formType=="text"){
                formHTML += makeFormElementText(element2);
    		}
    	});
	    formHTML += "</form></div>";
	    $("#footage").append(formHTML);
    });
    loadClicks();
}

function loadClicks(){

	$("#entitiesList ul li").click(function(){
		if($(this).hasClass("selected")){
			removeFilter($(this).attr("entity_id"));
		}else{
			loadFilter($(this).data("filter"), $(this).attr("entity_id"),$(this).attr("eid"));
		}
		$(this).toggleClass("selected");
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

}

function sumarizeFilter(object){

	summaryHTML = "";
	$.each(filtersLiteralOutputArray[object.parent().attr("eid")], function(nom, valors) {
		summaryHTML += "<b>" + nom +"</b>" + valors+"</br>";
    });
	object.find(".filterSummary").html(summaryHTML);

}

function showFilterData(results, entity_filter,filterName,eid){
	filtersArray.push(entity_filter);
	filterPosition = filtersArray.indexOf(entity_filter);
	$('#filterModel').clone(true).appendTo("#filterArea").attr("id","filter_"+filterPosition).attr("class","entity_"+entity_filter).attr("eid",eid);
	$('#filterArea').width(480+(filtersArray.length*780));
	newFilter = "#filter_"+filterPosition;
    $(newFilter).find(".filterList").append(listFilterData(results));
    $(newFilter).find(".filterList ul li").click(function(){
  		$(this).toggleClass("selected");
	});
    $(newFilter).find(".filterBall span").html(filterName);
    $(".form_"+entity_filter).clone(true).appendTo($(newFilter).find(".formFilter"));

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

function listFilterData(data){
    list = "<ul>";
    $.each(data, function(index, element) {
        if (element.name) {
            list += "<li>"+element.name+"</li>";
        } else {
            list += "<li>"+element.title+"</li>";
        }
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
		console.log(filtersLiteralOutputArray);
		//console.log(filtersOutputArray);

	}
