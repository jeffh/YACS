(function($, _, window, document, undefined){

var History = window.History;

var schedules_template, no_schedules_template, too_many_crns_template, period_height;
if ($('#schedule-template').length){
    schedules_template = _.template($('#schedule-template').html());
    no_schedules_template = _.template($('#no-schedules-template').html());
    too_many_crns_template = _.template($('#too-many-crns-template').html());
    period_height = parseInt($('#schedule-template').attr('data-period-height'), 10);
}

function url_with_sid(sid){
    var url = window.location.href;
    if(url.indexOf('&schedule=') >= 0 || url.indexOf('?schedule=') >= 0){
        url = url.replace(/([&?])schedule=(.*)(&?)/, "$1schedule=" + sid + '$3');
        return url.replace(/#schedule(\d+)/, "#schedule=" + sid);
    }
    if(url.indexOf('?') >= 0){
        url += '&schedule=' + sid;
        return url + '#schedule' + sid;
    }
    url += '?schedule=' + sid;
    return url + '#schedule' + sid;
}

function next_schedule(){
    if($(this).hasClass('disabled'))
        return false;
    var sid = $(this).closest('.schedule_wrapper').hide().next().show().attr('data-sid');
    if(History.enabled){
        History.pushState({schedule: sid}, null, url_with_sid(sid));
    }
    return false;
}
function prev_schedule(){
    if($(this).hasClass('disabled'))
        return false;
    var sid = $(this).closest('.schedule_wrapper').hide().prev().show().attr('data-sid');
    if(History.enabled){
        History.pushState({schedule: sid}, null, url_with_sid(sid));
    }
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
    if (minutes !== 0)
        return hour + ":" + (minutes < 10 ? '0' : '') + minutes + apm;
    return hour + apm;
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

function get_schedule_id_from_state(){

    var selected_schedule = 0;
    // history !!!!!!!! ^_^ ^_^ ^_^
    if (History.enabled){
        var state = History.getState(),
            schedule = parseInt(state.data.schedule, 10);
        console.log(History.getHash());
        if(isNaN(schedule)){
            var hash = History.getHash(),
                i = hash.indexOf('schedule');
            schedule = 1;
            if(i >= 0){
                var match = hash.match(/schedule(\d+)/);
                if(match){
                    schedule = parseInt(match[1], 10);
                }
            }
        }
        selected_schedule = (schedule || 1) - 1;
    }
    return selected_schedule;
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

    console.log(context);

    var selected_schedule = get_schedule_id_from_state();

    renderers = [];
    $('#schedules').html('');
    var create_renderer = function(schedule, i){
        return function(){
            context.sid = i + 1;
            context.schedule = schedule;
            var frag = $(schedules_template(context));
            if (i !== selected_schedule) $(frag).hide();
            $('#schedules').append(frag);
            console.log('rendering ' + (i+1) + ' of ' + context.schedules.length);
        };
    }
    _.forEach(context.schedules, function(schedule, i){
        renderers.push(setTimeout(create_renderer(schedule, i), 10 * i));
    });
}

function get_schedules(){
    var url = $('#schedules').attr('data-source');
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
        error: function(xhr, status){
            // TODO: show a custom error page
            if(xhr.status === 403){
                $('#schedules').html(too_many_crns_template({}));
            } else
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

    History.Adapter.bind(window, 'statechange', function(){
        var state = History.getState();
        var selected_schedule = (parseInt(state.data.schedule, 10) || 1) - 1;
        $($('.schedule_wrapper').hide().get(selected_schedule)).show();
    });

    History.Adapter.trigger(window, 'statechange')


});

})(jQuery, _, window, document);
