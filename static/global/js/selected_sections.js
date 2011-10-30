(function($, window, document, undefined){

var animation_duration = 250;
var selected_courses = {}; // course_id => crns

var updateFuse = new Utils.Fuse({
    delay: 150,
    execute: function(){
        var parameters = {}, selected_crns = [];
        $.each(selected_courses, function(cid, crns){
            parameters['selected_course_' + cid] = "checked";
            $.each(crns, function(i, crn){
                parameters['selected_course_' + cid + '_' + crn] = "checked";
                selected_crns.push(crn);
            });
        });
        console.log('post', parameters);
        $.ajax(Utils.selectURL(), {
            type: "post",
            data: $.param(parameters),
            complete: function(){
                $('.tinyspinner').fadeOut({duration:animation_duration});
                // should we show an error???
            }
        });

        $.ajax(Utils.checkScheduleURL() + '?check=1&crn=' + selected_crns.join('&crn='), {
            type: "get",
            success: function(){
                console.log('ok');
            },
            error: function(){
                alert('This course causes conflicts (no possible schedules).');
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
    if($.inArray(crn, selected_courses[courseID]) !== -1)
        return;
    selected_courses[courseID].push(crn);
    updateFuse.start();
    // TODO: see if schedules exist...
}

function removeSectionFromSelection(courseID, crn){
    courseID = String(courseID);
    crn = parseInt(crn, 10);
    if(!selected_courses[courseID]){
        console.log('no sections were selected in course ' + courseID);
        return;
    }
    updateFuse.stop();
    if($.inArray(crn, selected_courses[courseID]) === -1){
        console.log(crn, 'not in', courseID);
        return;
    }
    selected_courses[courseID].removeItem(crn);
    if(selected_courses[courseID].length === 0)
        delete selected_courses[courseID];
    updateFuse.start();
}

function syncSelection(){
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
    console.log($(this).parents('.course').length);
    $(this).parents('.course').find('.tinyspinner').fadeIn({duration:animation_duration});

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

    $el.parents('.course').find('.tinyspinner').fadeIn({duration:animation_duration});
    if (!el.checked){
        removeFromSelected($el);
        // remove from selected
        return;
    }
    // add to selected
    addToSelected($el);
}

// initialization
$(function(){
    $('#selected .course > input[type=checkbox]').live('change', courseChanged);
    $('#selected .section input[type=checkbox]').live('change', sectionChanged);
    $('.save-selected').hide(); // selected courses save button

    // hide add to selection button... autoadd on check
    $('#courses').live('change', courseSelected);
    $('#courses input[type=submit]').hide();

    syncSelection();
});

})(jQuery, window, document);
