(function($, window, document, undefined){


function next_schedule(){
    if($(this).hasClass('disabled'))
        return false;
    $(this).closest('.schedule_wrapper').hide().next().show();
    return false;
}
function prev_schedule(){
    if($(this).hasClass('disabled'))
        return false;
    $(this).closest('.schedule_wrapper').hide().prev().show();
    return false;
}

$(function(){
    $('.schedule_wrapper').hide();
    $('.schedule_wrapper:first').show();
    $('.prev-schedule').click(prev_schedule);
    $('.next-schedule').click(next_schedule);
});

})(jQuery, window, document);
