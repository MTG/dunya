$(document).ready(function() {
    $("#statehandle").click(function(e) {
        e.preventDefault();
        $("#statebox").slideToggle();
    });

    $(".showhidden").click(function(e) {
        e.preventDefault();
        var checkerid = $(this).data("tohide");
        $(".tohide"+checkerid).slideToggle({duration:0});
    });
});

