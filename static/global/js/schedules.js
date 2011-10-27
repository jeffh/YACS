(function($, _, window, document, undefined){

var schedules_template, no_schedules_template, period_height;
if ($('#schedule-template').length){
    schedules_template = _.template($('#schedule-template').html());
    no_schedules_template = _.template($('#no-schedules-template').html());
    period_height = parseInt($('#schedule-template').attr('data-period-height'), 10);
}

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

// template rendering

function time_parts(timestr){
    var parts = timestr.split(':'); // hour:min:sec
    return {
        hour: parseInt(parts[0], 10),
        minute: parseInt(parts[1], 10),
        second: parseInt(parts[2], 10)
    };
}

function time_to_seconds(timestr){
    var parts = time_parts(timestr); // hour:min:sec
    return parts.hour * 3600 + parts.minute * 60 + parts.second;
}

function get_crns(schedule){
    return _.values(schedule);
}

function create_color_map(context, maxcolors){
    var color_map = {},
        schedule = context.schedules[0],
        maxcolors = maxcolors || 9;
    ++maxcolors;
    _.forEach(_.keys(schedule), function(cid, i){
        color_map[cid] = (i % maxcolors) + 1;
    });
    return color_map;
}

function humanize_time(timestr){
    var parts = timestr.split(':'),
        hour = parseInt(parts[0], 10),
        minutes = parseInt(parts[1], 10),
        apm = 'am';
    if (hour === 0)
        hour = 12;
    if (hour > 12){
        apm = 'pm';
        hour = hour - 12;
    }
    return hour + ":" + (minutes < 10 ? '0' : '') + minutes + " " + apm;
}

function humanize_hour(hour){
    var apm = 'am'
    if (hour == 0)
        hour = 12
    if (hour >= 12)
        apm = 'pm'
    if (hour > 12)
        hour = hour - 12
    return hour + " " + apm;
}

function get_period_offset(period){
    var start = time_parts(period.start_time),
        time = start.minute * 60 + start.second;
    return time / 3600.0 * period_height;
}

function get_period_height(period){
    var time = time_to_seconds(period.end_time) - time_to_seconds(period.start_time);
    //return 25 // 30 min time block
    //return 41.666666667 // 50 min time block
    return time / 3600.0 * period_height;
}

var renderers = [];
function show_schedules(context){
    context.humanize_time = humanize_time;
    context.get_period_height = get_period_height;
    context.get_period_offset = get_period_offset;
    context.get_crns = get_crns;
    context.color_map = create_color_map(context);
    context.humanize_hour = humanize_hour;
    _.forEach(renderers, function(timeout){
        clearTimeout(timeout);
    });
    renderers = [];
    $('#schedules').html('');
    var create_renderer = function(schedule, i){
        return function(){
            context.sid = i + 1;
            context.schedule = schedule;
            var frag = $(schedules_template(context));
            if (i !== 0) $(frag).hide();
            $('#schedules').append(frag);
            console.log('rendering', i+1, 'of', context.schedules.length);
        };
    }
    _.forEach(context.schedules, function(schedule, i){
        renderers.push(setTimeout(create_renderer(schedule, i), 10 * i));
    });
}

function get_schedules(){
    var url = $('#schedules').attr('data-source');
    console.log(url);
    if(!url) return;
    $.ajax(url, {
        type: 'GET',
        dataType: 'json',
        success: function(json){
            if(json.schedules && json.schedules.length){
                show_schedules(json);
                return;
            }
            // ERROR
            $('#schedules').html(no_schedules_template({}));
        },
        error: function(){
            // TODO: show a custom error page
            alert('Failed to get schedules... (are you connected to the internet?)');
        }
    });
}

function schedules_loaded(){
    $('.schedule_wrapper').hide();
    $('.schedule_wrapper:first').show();
    $('.prev-schedule').live('click', prev_schedule);
    $('.next-schedule').live('click', next_schedule);
}

$(function(){
    schedules_loaded();
    get_schedules();
});

})(jQuery, _, window, document);
