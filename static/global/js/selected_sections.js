(function($, window, document, undefined){

var animation_duration = 250;
var selected_courses = {}; // course_id => crns
window.selected_courses = selected_courses;
var undoHistory = [];

function saveSelection(){
    var parameters = {}, selected_crns = [];
    $.each(selected_courses, function(cid, crns){
        parameters['selected_course_' + cid] = "checked";
        $.each(crns, function(i, crn){
            parameters['selected_course_' + cid + '_' + crn] = "checked";
            selected_crns.push(crn);
        });
    });

    $.ajax(Utils.selectURL(), {
        type: "post",
        data: $.param(parameters),
        complete: function(){
            // should we show an error???
        }
    });
    return selected_crns;
}

var updateFuse = new Utils.Fuse({
    delay: 150,
    execute: function(){
        var selected_crns = saveSelection();

        $.ajax(Utils.checkScheduleURL() + '?check=1&crn=' + selected_crns.join('&crn='), {
            type: "get",
            complete: function(){
                $('.tinyspinner').fadeOut({duration:animation_duration});
            },
            error: function(xhr, status){
                if(xhr.status === 403){
                    alert('Too many sections for YACS to handle (for now).');
                } else if(xhr.status === 404) {
                    alert('This course causes conflicts (no possible schedules).');
                } else {
                    alert('Failed to save to the server...')
                }
                var undoer = undoHistory.pop();
                if(undoer){
                    undoer();
                }
            }
        })
    }
});

// lower level operations to modify the selection, should automatically
// handle syncing with the server
function addSectionToSelection(courseID, crn){
    courseID = parseInt(courseID, 10);
    crn = parseInt(crn, 10);
    updateFuse.stop();
    if(!selected_courses[courseID])
        selected_courses[courseID] = [];
    if($.inArray(crn, selected_courses[courseID]) !== -1){
        $('.tinyspinner').fadeOut({duration:animation_duration});
        return;
    }
    selected_courses[courseID].push(crn);
    updateFuse.start();
    // TODO: see if schedules exist...
}

function removeSectionFromSelection(courseID, crn){
    courseID = String(courseID);
    crn = parseInt(crn, 10);
    if(!selected_courses[courseID]){
        console.log('no sections were selected in course ' + courseID);
        $('.tinyspinner').fadeOut({duration: animation_duration});
        return;
    }
    updateFuse.stop();
    if($.inArray(crn, selected_courses[courseID]) === -1){
        console.log(crn, 'not in', courseID);
        $('.tinyspinner').fadeOut({duration: animation_duration});
        return;
    }
    selected_courses[courseID].removeItem(crn);
    if(selected_courses[courseID].length === 0)
        delete selected_courses[courseID];
    updateFuse.start();
}

function getSelection(){
    $.ajax(Utils.selectionURL(), {
        type: 'GET',
        dataType: 'text',
        success: function(content, status, request){
            var selection = Utils.json(content);
            updateFuse.freeze();
            $.each(selection, function(cid, crns){
                $.each(crns, function(i, crn){
                    addSectionToSelection(cid, crn);
                });
            });
            updateFuse.thaw();
            // TODO: update
        },
        error: function(request, status, error){

        }
    })
}

// end selection handling

// event handling for #selected
function sectionChanged(evt){
    // update selection via ajax ???
    var crn = $(this).attr('data-crn'), courseID = $(this).attr('data-cid');
    $(this).parents('.course').find('.tinyspinner').fadeIn({duration:animation_duration});

    undoHistory.push((function($el){
        var state = $.extend(true, {}, selected_courses);
        return function(){
            selected_courses = state;
            $el.removeAttr('checked');
            saveSelection();
        };
    })($(this)));

    if (this.checked){
        addSectionToSelection(courseID, crn);
        // check parent if not done so
        $(this).parents('.course').find('input[type=checkbox]:first').attr('checked', 'checked');
        return;
    }

    removeSectionFromSelection(courseID, crn);
}

function courseChanged(evt){
    var $sections = $(this).parent().find('.section input[type=checkbox]');
    if (this.checked)
        $sections.attr('checked', 'checked');
    else
        $sections.removeAttr('checked');

    undoHistory.push((function($el){
        var state = $.extend(true, {}, selected_courses);
        return function(){
            selected_courses = state;
            $el.removeAttr('checked');
            saveSelection();
        };
    })($sections));

    $sections.each(function(){
        sectionChanged.call(this, evt);
    });
}

// handles adding & removing selections by (un)checking the courses in #courses.
function addToSelected($course){
    var courseID = $course.attr('data-cid'),
        crns = Utils.splitNonEmpty($course.attr('data-crns')),
        fullCrns = Utils.splitNonEmpty($course.attr('data-crns-full')),
        availableCrns = Utils.setDifference(crns, fullCrns);

    $.each(availableCrns, function(){
        addSectionToSelection(courseID, this);
    });

    if(availableCrns.length === 0){
        $('.tinyspinner').fadeOut({duration: animation_duration});
    }
}

function removeFromSelected($course){
    var courseID = $course.attr('data-cid'),
        crns = Utils.splitNonEmpty($course.attr('data-crns'));

    $.each(crns, function(){
        removeSectionFromSelection(courseID, this);
    });
}
// end selection GUI modifiers

// event handling for #courses
function courseSelected(evt){
    var el = evt.target, $el = $(el);
    if (!$el.is('input[type=checkbox]'))
        return;

    undoHistory.push((function($el){
        var state = $.extend(true, {}, selected_courses);
        return function(){
            selected_courses = state;
            $el.removeAttr('checked');
            saveSelection();
        };
    })($el));

    $el.parents('.course').find('.tinyspinner').fadeIn({duration:animation_duration});
    if (!el.checked){
        removeFromSelected($el);
        // remove from selected
        return;
    }
    // add to selected
    addToSelected($el);
}

function labelize(evt){
    var $el = $(evt.target), $forel = $('#'+$el.attr('for'));
    if($forel.is('input[type=radio], input[type=checkbox]')){
        $forel.attr('selected', !$forel.attr('selected'));
        return;
    }
    $forel.focus();
}

// initialization
$(function(){
    $('#selected_courses .course > input[type=checkbox]').live('change', courseChanged);
    $('#selected_courses .section input[type=checkbox]').live('change', sectionChanged);
    $('.save-selected').hide(); // selected courses save button

    // hide add to selection button... autoadd on check
    $('#courses').live('change', courseSelected);
    $('#courses input[type=submit]').hide();

    // iOS doesn't support label touch... so we have to simulate it
    if (navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPod/i) || navigator.userAgent.match(/iPad/i)) {
        $('label').click(labelize);
    }

    getSelection();
});

})(jQuery, window, document);
