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

// function parseAllFilters(){
//    $.each(window.filtersItems, function(index, element) {
//    	entityHTML = "<li class='entity_"+(index+1)+"' entity_id='"+(index+1)+"' eid='eid"+(index+1)+"'><div class='colorCode shadow1'></div>"+element.name+"</li>";
//    	$("#entitiesList ul").append(entityHTML);
//    	formHTML = "<div class='form_"+(index+1)+"'><form>";
//
var makeFormElementList = function(element) {
    if (element.multiselect) {
        var filtertype = 'multiSelect';
    } else {
        var filtertype = 'select';
    }
    var fieldset = $("<fieldset>").data("type", filtertype).data("name", element.name);
    fieldset.append($("<label>", {"class": "formSection"}).text(element.name));

    var div = $("<div>", {"class": "filterList formFilterItem"});
    var ul = $("<ul>");
    for( i in element.data ){
        var li = $("<li>").data("id", i+1).data("value", element.data[i]).text(element.data[i]);
        ul.append(li);
    }
    div.append(ul);
    fieldset.append(div);
    return fieldset;
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
    form = $("<form>").data("type", "text").data("name", element.name);
    form.append(
            $("<label>", {"class": "formSectionText"})
                .append(element.name)
                .append($("<input>", {type:"text"}))
            );
    return form;
};

function parseAllFilters(filtersItems){
    $.each(filtersItems, function(index, element) {
        console.log(element.name)
        var entity = $("<li>", {
            entity_id: (index+1),
            class: "entity_"+(index+1),
            eid: "eid"+(index+1)
        }).append($("<div>", {"class": "colorCode shadow1"}))
          .append(element.name);
        entity.data("filter", element);

	    $("#entitiesList ul").append(entity);
        form = $("<form>").append(element.name);
    	$.each(element.data, function(index2, element2) {
    		formType = element2.type;
    		if (formType=="list") {
                form.append(makeFormElementList(element2));
    		} else if (formType=="rangeslider") {
                form.append(makeFormElementSlider(element2));
    		} else if (formType=="text") {
                form.append(makeFormElementText(element2));
    		}
    	});
	    $("#footage").append($("<div>", {"class": "form_"+(index+1)}).append(form));
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
			loadFilter($(this).data("filter"), $(this).attr("entity_id"),$(this).attr("eid"));
		}
		$(this).toggleClass("selected");
		$("#summary").attr("class","entity_"+$(this).attr("entity_id"));
	});

	$(".filterList.formFilterItem ul li").click(function(){
		$(this).toggleClass("selected");
		//getResults($(this));
        performSearch();
	});

	$(".formSection").click(function(){
		$(this).toggleClass("formSectionOpen");
		$(this).nextAll(".formFilterItem").toggle();
		$(".formSection").not(this).removeClass("formSectionOpen");
		$(".formSection").not(this).nextAll(".formFilterItem").hide();
		topPosition = $(this).position()
		container = $(this).parent().parent().parent().parent();
		container.scrollTop(topPosition.top-10);
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
    return

	summaryHTML = "";
	$.each(filtersLiteralOutputArray[object.parent().attr("eid")], function(nom, valors) {
		summaryHTML += "<b>" + nom +"</b>" + valors+"</br>";
    });
	object.find(".filterSummary").html(summaryHTML);

}

function showFilterData(results, entity_filter,filterName,eid){
	filtersArray.push(entity_filter);
	filterPosition = filtersArray.indexOf(entity_filter);
	$('#filterModel').clone(true).appendTo("#filterArea").attr("id","filter_"+filterPosition).attr("class","filters entity_"+entity_filter).attr("eid",eid);
	entityHTML_bc = "<div class='bread entity_"+entity_filter+"'><div class='breadarrow'></div><span><a href='#'>No selection</a></span></div>";
	$("#breadcrumb").append(entityHTML_bc);
	$('#filterModel').clone(true).appendTo("#filterArea").attr("id","filter_"+filterName).attr("class","entity_"+entity_filter).attr("eid",eid);
	$('#filterArea').width(480+(filtersArray.length*780));
	newFilter = "#filter_"+filterName;
    $(newFilter).find(".filterList").append(listFilterData(results));
    $(newFilter).find(".filterList ul li").click(function(){
  		$(this).toggleClass("selected");
  		$("#breadcrumb").find(".entity_"+entity_filter+" span a").html($(this).html());
	});
    $(newFilter).find(".filterBall span").html(filterName);
    $(".form_"+entity_filter).clone(true).appendTo($(newFilter).find(".formFilter"));

    $(newFilter+" .formFilter").removeClass("formFilterClosed");
	$(newFilter+" .filterList").removeClass("filterListClosed");
	$(newFilter+" .filterBall .arrow").removeClass("arrowClosed");
	$(newFilter+" .filterBall").removeClass("filterBallClosed");

    $(newFilter+" .slider-range").each(function(){
        var sliderdata = {
			range: true,
			min: parseInt($(this).attr('min')),
			max: parseInt($(this).attr('max')),
			values: [ parseInt($(this).attr('min')), parseInt($(this).attr('max')) ],
			slide: function( event, ui ) {
				$(newFilter).find(".output").html( ui.values[ 0 ] + " - " + ui.values[ 1 ] + "<div class='results' first='"+ui.values[ 0 ]+"' second='"+ui.values[ 1 ]+"'></div>" );
			}
        };

    	if($(this).attr('step')) {
            sliderdata["step"] = parseInt($(this).attr('step'));
        }
        $(this).slider(sliderdata);
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

var updateSearchForEntity = function(entity) {
    // TODO: We only want to do a search update if the values have changed
    // since last time.
    var name = $(entity).data("filter").name;
    console.log("for entity " + name);
    var search = $("div#filter_"+name);

    search.find($("fieldset")).each(function(i, e) {
        var data = $(e).data()
        console.log("Criteria " + data.name)
        $(e).find("li.selected").each(function(j, li) {
            console.log("   "+$(li).data("value"));
        });
    });
};

var performSearch = function() {
    $.each($("div#entitiesList li.selected"), function (i, el) {
        updateSearchForEntity(el);
    });

};

function getResults(item) {
		var entity = item.parent().parent().parent().parent().parent().parent().parent().attr("eid");
		var filterType = item.parents("fieldset").data("type");
		var filterName = item.parents("fieldset").data("name");
		theValue = "";
		theName = "";
		if( filterType == "multiSelect" ){
			theValue =[ ];
			theName =[ ];
			item.parent().find(".selected").each(function (i){
        		theValue[i]=$(this).data("id");
        		theName[i]=$(this).data("value");
        		console.log(theName[i]);
        	});
		}else if( filterType == "select" ){
			theValue = item.parent().find(".selected").data("id");
			theName = item.parent().find(".selected").data("value");
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
