(function($, window, document, undefined){

window.Utils = {};

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.extend(Utils, {
    CSRFToken: function(){
        return getCookie('csrftoken');
    },
    splitNonEmpty: function(string, separator){
        separator = separator || ',';
        var result = [];
        $.each(string.split(','), function(){
            result.push(this);
        });
        return result;
    },
    setDifference: function(arr1, arr2){
        var result = [];
        $.each(arr1, function(){
            if(!$.inArray(this, arr2))
                result.push(this);
        });
        return result;
    },
    Fuse: function(options){
        var opt = $.extend({delay: 200, execute: function(){}}, options),
            self = this;
        this.options = opt;
        this.timer = null;
        this.isFrozen = false;

        this.stop = function(){
            if (self.timer){
                clearTimeout(self.timer);
                self.timer = null;
            }
        };

        this.freeze = function(){
            self.stop();
            self.isFrozen = true;
        };
        this.thaw = function(){
            self.isFrozen = false;
        };

        this.trigger = function(){
            self.stop();
            if(!self.isFrozen)
                self.options.execute.call(self);
        };

        this.start = function(){
            self.stop();
            if(!self.isFrozen)
                self.timer = setTimeout(self.trigger, self.options.delay);
        };
    }
});

// modify ajax requests to use csrf token for local POST requests
// taken from https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
$(document).ajaxSend(function(event, xhr, settings) {
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", Utils.CSRFToken());
    }
});

})(jQuery, window, document);
