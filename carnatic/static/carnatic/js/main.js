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
    $('#user').click(function() {
        $("#userOptions").show({easing: "easeInOutQuad"});
        $(this).find('#userOptions').addClass( "open", globalSpeed, "easeInOutQuad");
    });
    $('#user').mouseleave(function() {
        $("#userOptions").hide({easing: "easeInOutQuad"});
        $(this).find('#userOptions').removeClass( "open", globalSpeed, "easeInOutQuad");
    });
    $('#guest').click(function() {
        $("#guestOptions").show({easing: "easeInOutQuad"});
        $(this).find('#guestOptions').addClass( "open", globalSpeed, "easeInOutQuad");
    });
    $('#guest').mouseleave(function() {
        $("#guestOptions").hide({easing: "easeInOutQuad"});
        $(this).find('#guestOptions').removeClass( "open", globalSpeed, "easeInOutQuad");
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
