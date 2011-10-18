(function($, window, document, undefined){

var selection = {}; // course_id => crns
window.selection = selection;

var updateFuse = new Utils.Fuse({
    delay: 250,
    execute: function(){
        var parameters = {};
        $.each(selection, function(cid, crns){
            parameters['selected_course_' + cid] = "checked";
            $.each(crns, function(i, crn){
                parameters['selected_course_' + cid + '_' + crn] = "checked";
            });
        });
        console.log('post', parameters);
        $.ajax(Utils.selectURL(), {
            type: "post",
            data: $.param(parameters),
            complete: function(){
            }
        });
    }
});

// lower level operations to modify the selection, should automatically
// handle syncing with the server
function addSectionToSelection(courseID, crn){
    courseID = parseInt(courseID, 10);
    crn = parseInt(crn, 10);
    updateFuse.stop();
    if(!selection[courseID])
        selection[courseID] = [];
    if($.inArray(crn, selection[courseID]) !== -1)
        return;
    selection[courseID].push(crn);
    updateFuse.start();
}

function removeSectionFromSelection(courseID, crn){
    courseID = parseInt(courseID, 10);
    crn = parseInt(crn, 10);
    if(!selection[courseID])
        return;
    updateFuse.stop();
    if($.inArray(crn, selection[courseID]) === -1){
        console.log(crn, 'not in', courseID);
        return;
    }
    selection[courseID].removeItem(crn);
    if(selection[courseID].length === 0)
        delete selection[courseID];
    updateFuse.start();
}

function syncSelection(){
    $.ajax(Utils.selectionURL(), {
        type: 'GET',
        dataType: 'text',
        success: function(content, status, request){
            var sections = Utils.json(content);
            updateFuse.freeze();
            $.each(sections, function(){
                addSectionToSelection(this.course.id, this.crn);
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

    if (this.checked){
        addSectionToSelection(courseID, crn);
        // check parent if not done so
        $(this).parent('.course').find('input[type=checkbox]:first').attr('checked', 'checked');
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
        console.log($(this).attr('data-crn'), this);
        sectionChanged.call(this, evt);
    });
}

// handles adding & removing selections by (un)checking the courses in #courses.
function addToSelected($course){
    console.log('add', $course.attr('data-cid'));
    var courseID = $course.attr('data-cid'),
        crns = Utils.splitNonEmpty($course.attr('data-crns')),
        fullCrns = Utils.splitNonEmpty($course.attr('data-crns-full')),
        availableCrns = Utils.setDifference(crns, fullCrns);
    $.each(availableCrns, function(){
        addSectionToSelection(courseID, this);
    });
}

function removeFromSelected($course){
    console.log('remove', $course.attr('data-cid'));
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
