// Avoid `console` errors in browsers that lack a console.
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());

// Place any jQuery/helper plugins in here.



function widthOfChildren(object){
	/*$(object).each(function(){
		var sum=0;
		$(this).children('div').each( function(){ sum += ($('div',this).width()+5); });
		$(this).width( sum+10 );
	});*/
	var sum=0;
	$(object+'>div').each( function(){ sum += ($(this).outerWidth()+5); });
	$(object).width( sum+10 );
	
}