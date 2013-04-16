// jquery boilerplate from http://stefangabos.ro/jquery/jquery-plugin-boilerplate-oop/
// run as var myplugin = new $.dunyaSearch($('#element'));
;(function($) {


    $.dunyaSearch = function(el, options) {

        // plugin's default options
        // this is private property and is accessible only from inside the plugin
        var defaults = {
            propertyName: 'value',
        }

        // to avoid confusions, use "plugin" instead of "this"
        var plugin = this;

        // hold defaults + provided settings
        plugin.settings = {}

        var init = function() {
            plugin.settings = $.extend({}, defaults, options);
            plugin.el = el;
            // init
        }

        // public methods
        // these methods can be called like:
        // plugin.methodName(arg1, arg2, ... argn) from inside the plugin or
        // myplugin.publicMethod(arg1, arg2, ... argn) from outside the plugin
        // where "myplugin" is an instance of the plugin

        // a public method. for demonstration purposes only - remove it!
        plugin.foo_public_method = function() {

            // code goes here

        }

        // private methods
        // these methods can be called only from inside the plugin like:
        // methodName(arg1, arg2, ... argn)

        // a private method. for demonstration purposes only - remove it!
        var foo_private_method = function() {

            // code goes here

        }

        init();
    }
})(jQuery);
