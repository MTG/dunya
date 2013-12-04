var globalSpeed  = 500;

$(document).ready(function() {
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
//    $.ajaxSetup({
//        crossDomain: false, // obviates need for sameOrigin test
//        beforeSend: function(xhr, settings) {
//        if (!csrfSafeMethod(settings.type)) {
//            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
//        }
//        }
//    });
	var myTimer=false;
	$("#userOptions").hover(function(){ clearTimeout(myTimer);});
	$("#guestOptions").hover(function(){ clearTimeout(myTimer);});
    $('#user').click(function() {
        $("#userOptions").show({easing: "easeInOutQuad"});
        $(this).find('#userOptions').addClass( "open", globalSpeed, "easeInOutQuad");
    });
    $('#user').mouseleave(function() {
		myTimer = setTimeout(function(){
			$("#userOptions").hide({easing: "easeInOutQuad"});
			$(this).find('#userOptions').removeClass( "open", globalSpeed, "easeInOutQuad");
		}, 500)
    });
    $('#guest').click(function() {
        $("#guestOptions").show({easing: "easeInOutQuad"});
        $(this).find('#guestOptions').addClass( "open", globalSpeed, "easeInOutQuad");
    });
    $('#guest').mouseleave(function() {
		myTimer = setTimeout(function(){
			$("#guestOptions").hide({easing: "easeInOutQuad"});
			$(this).find('#guestOptions').removeClass( "open", globalSpeed, "easeInOutQuad");
		}, 500)
    });

    $("#searchbox").autocomplete({
        source: "/carnatic/searchcomplete",
        minlength: 2,
        select: function(event, ui) {
            console.debug("select");
            console.debug(ui);
        }
    });

    // When you click on the (+) on a badge, expand it open
    $(".inforight .desc .plus").click(function(){
        $(this).parent().parent().toggleClass("open");
        $('.scrollblock').isotope('reLayout');
    });

});
