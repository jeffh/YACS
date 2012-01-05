(function($, window, document){

$(function(){
    // hide selected if we have javascript enabled.
    // TODO: reveal at certain larger screen widths, and hide the button from the nav
    if (!$('.selected-courses').hasClass('selected')){
        $('#selected').hide();
    }
});

})(jQuery, window, document);
