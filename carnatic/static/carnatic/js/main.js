var globalSpeed  = 500;

$(document).ready(function() {

	$('.item .similarity div').click(function(){
    $('.item .similarity div').removeClass('active');
      theparent = $(this).parent();
      buscar = ".right ."+$(this).attr('class');
      theparent.parent().parent().find(".right .similarList").removeClass('active');
      theparent.parent().parent().find(buscar).addClass('active');
      theparent.parent().parent().find(".right").fadeIn('slow');
      $(this).addClass("active");
    });

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
