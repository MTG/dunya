var globalSpeed  = 500;

$(document).ready(function() {
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
	var myTimer=false;
	$("#usermenuoptions").hover(function(){ clearTimeout(myTimer);});
    $('#usermenu').click(function() {
        $("#usermenuoptions").show({easing: "easeInOutQuad"});
        $(this).find('#usermenuoptions').addClass("open", globalSpeed, "easeInOutQuad");
    });
    $('#usermenu').mouseleave(function() {
		myTimer = setTimeout(function(){
			$("#usermenuoptions").hide({easing: "easeInOutQuad"});
			$(this).find('#usermenuoptions').removeClass("open", globalSpeed, "easeInOutQuad");
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
});
