// Plugins

// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
log.history = log.history || [];   // store logs to an array for reference
log.history.push(arguments);
arguments.callee = arguments.callee.caller;
if(this.console) console.log( Array.prototype.slice.call(arguments) );
};

// make it safe to use console.log always
(function(b){function c(){}for(var d="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),a;a=d.pop();)b[a]=b[a]||c})(window.console=window.console||{});

// jQuery/helper plugins

/*!
 * HTML5 Placeholder jQuery Plugin v1.8.2
 * @link http://github.com/mathiasbynens/Placeholder-jQuery-Plugin
 * @author Mathias Bynens <http://mathiasbynens.be/>
 */

;(function($) {

    var isInputSupported = 'placeholder' in document.createElement('input'),
        isTextareaSupported = 'placeholder' in document.createElement('textarea');
    if (isInputSupported && isTextareaSupported) {
        $.fn.placeholder = function() {
            return this;
        };
        $.fn.placeholder.input = $.fn.placeholder.textarea = true;
    } else {
        $.fn.placeholder = function() {
            return this.filter((isInputSupported ? 'textarea' : ':input') + '[placeholder]')
                .bind('focus.placeholder', clearPlaceholder)
                .bind('blur.placeholder', setPlaceholder)
            .trigger('blur.placeholder').end();
        };
        $.fn.placeholder.input = isInputSupported;
        $.fn.placeholder.textarea = isTextareaSupported;
    }

    function args(elem) {
        // Return an object of element attributes
        var newAttrs = {},
            rinlinejQuery = /^jQuery\d+$/;
        $.each(elem.attributes, function(i, attr) {
            if (attr.specified && !rinlinejQuery.test(attr.name)) {
                newAttrs[attr.name] = attr.value;
            }
        });
        return newAttrs;
    }

    function clearPlaceholder() {
        var $input = $(this);
        if ($input.val() === $input.attr('placeholder') && $input.hasClass('placeholder')) {
            if ($input.data('placeholder-password')) {
                $input.hide().next().attr('id', $input.removeAttr('id').data('placeholder-id')).show().focus();
            } else {
                $input.val('').removeClass('placeholder');
            }
        }
    }

    function setPlaceholder(elem) {
        var $replacement,
            $input = $(this),
            $origInput = $input,
            id = this.id;
        if ($input.val() === '') {
            if ($input.is(':password')) {
                if (!$input.data('placeholder-textinput')) {
                    try {
                        $replacement = $input.clone().attr({ type: 'text' });
                    } catch(e) {
                        $replacement = $('<input>').attr($.extend(args(this), { type: 'text' }));
                    }
                    $replacement
                        .removeAttr('name')
                        // We could just use the `.data(obj)` syntax here, but that wouldn’t work in pre-1.4.3 jQueries
                        .data('placeholder-password', true)
                        .data('placeholder-id', id)
                        .bind('focus.placeholder', clearPlaceholder);
                    $input
                        .data('placeholder-textinput', $replacement)
                        .data('placeholder-id', id)
                        .before($replacement);
                }
                $input = $input.removeAttr('id').hide().prev().attr('id', id).show();
            }
            $input.addClass('placeholder').val($input.attr('placeholder'));
        } else {
            $input.removeClass('placeholder');
        }
    }

    $(function() {
        // Look for forms
        $('form').bind('submit.placeholder', function() {
            // Clear the placeholder values so they don’t get submitted
            var $inputs = $('.placeholder', this).each(clearPlaceholder);
            setTimeout(function() {
                $inputs.each(setPlaceholder);
            }, 10);
        });
    });

    // Clear placeholder values upon page reload
    $(window).bind('unload.placeholder', function() {
        $('.placeholder').val('');
    });

}(jQuery));

// http://unstoppablerobotninja.com/entry/fluid-images/
var imgSizer = {
     Config : {
          imgCache : []
          ,spacer : "/path/to/your/spacer.gif"
     }
     ,collate : function(aScope) {
          var isOldIE = (document.all && !window.opera && !window.XDomainRequest) ? 1 : 0;
          if (isOldIE && document.getElementsByTagName) {
               var c = imgSizer;
               var imgCache = c.Config.imgCache;
               var images = (aScope && aScope.length) ? aScope : document.getElementsByTagName("img");
               for (var i = 0; i < images.length; i++) {
                    images.origWidth = images.offsetWidth;
                    images.origHeight = images.offsetHeight;
                    imgCache.push(images);
                    c.ieAlpha(images);
                    images.style.width = "100%";
               }
               if (imgCache.length) {
                    c.resize(function() {
                         for (var i = 0; i < imgCache.length; i++) {
                              var ratio = (imgCache.offsetWidth / imgCache.origWidth);
                              imgCache.style.height = (imgCache.origHeight * ratio) + "px";
                         }
                    });
               }
          }
     }
     ,ieAlpha : function(img) {
          var c = imgSizer;
          if (img.oldSrc) {
               img.src = img.oldSrc;
          }
          var src = img.src;
          img.style.width = img.offsetWidth + "px";
          img.style.height = img.offsetHeight + "px";
          img.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + src + "', sizingMethod='scale')"
          img.oldSrc = src;
          img.src = c.Config.spacer;
     }
     // Ghettomodified version of Simon Willison's addLoadEvent() -- http://simonwillison.net/2004/May/26/addLoadEvent/
     ,resize : function(func) {
          var oldonresize = window.onresize;
          if (typeof window.onresize != 'function') {
               window.onresize = func;
          } else {
               window.onresize = function() {
                    if (oldonresize) {
                         oldonresize();
                    }
                    func();
               }
          }
     }
}
$(function(){
     if (document.getElementById && document.getElementsByTagName) {
          var aImgs = $('.content').get(0);
          if (!aImgs) return;
          aImgs.getElementsByTagName("img");
          imgSizer.collate(aImgs);
     }
})

if (navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPad/i)) {
var viewportmeta = document.querySelectorAll('meta[name="viewport"]')[0];
if (viewportmeta) {
viewportmeta.content = 'width=device-width, minimum-scale=1.0, maximum-scale=1.0';
document.body.addEventListener('gesturestart', function() {
viewportmeta.content = 'width=device-width, minimum-scale=0.25, maximum-scale=1.6';
}, false);
}
}
