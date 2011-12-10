(function($, window, document, undefined){

function SelectedCourses(options){
    var self = this;
    var options = $.extend({
        saveURL: Utils.selectURL(),
        fetchURL: Utils.selectionURL(),
        verifyScheduleURL: Utils.checkScheduleURL(),
        onSaveComplete: function(){}
    }, options || {}),
        saveRequest = null,
        updateRequest = null,
        selection = {},
        undoHistory = [];

    var updateFuse = new Utils.Fuse({
        delay: 50,
        execute: function(){
            var selected_crns = self.save();

            if(updateRequest)
                updateRequest.abort();

            updateRequest = $.ajax(options.verifyScheduleURL + '?check=1&crn=' + selected_crns.join('&crn='), {
                cache: false,
                type: "get",
                complete: function(){
                    //$('.tinyspinner').fadeOut({duration:options.animationDuration});
                    options.onSaveComplete();
                    updateRequest = undefined;
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

    $.extend(self, {
        options: options,

        getSelection: function(){
            return selection;
        },
        setSelection: function(newSelection){
            selection = newSelection;
        },
        saveStateForUndo: function(fn){
            undoHistory.push((function(){
                var state = $.extend(true, {}, self.getSelection());
                return function(){
                    self.setSelection(state);
                    if($.isFunction(fn))
                        fn();
                    self.save();
                };
            })());
        },
        save: function(){
            var parameters = {}, selected_crns = [];
            $.each(selection, function(cid, crns){
                parameters['selected_course_' + cid] = "checked";
                $.each(crns, function(i, crn){
                    parameters['selected_course_' + cid + '_' + crn] = "checked";
                    selected_crns.push(crn);
                });
            });

            if (saveRequest)
                saveRequest.abort();

            saveRequest = $.ajax(options.saveURL, {
                cache: false,
                type: "post",
                data: $.param(parameters),
                complete: function(){
                    // should we show an error???
                    saveRequest = undefined;
                }
            });
            return selected_crns;
        },
        fetch: function(){
            $.ajax(options.fetchURL, {
                cache: false,
                type: 'GET',
                dataType: 'text',
                success: function(content, status, request){
                    var selection = Utils.json(content);
                    updateFuse.freeze();
                    $.each(selection, function(cid, crns){
                        $.each(crns, function(i, crn){
                            self.add(cid, crn);
                        });
                    });
                    updateFuse.thaw();
                    // TODO: update
                },
                error: function(request, status, error){

                }
            });
        },
        getCourseIDByCRN: function(crn){
            var result = undefined;
            $.each(selection, function(courseID, crns){
                if($.inArray(crn, crns) !== -1){
                    result = courseID;
                    return false;
                }
            });
            return result;
        },
        add: function(courseID, crn){
            courseID = parseInt(courseID, 10);
            crn = parseInt(crn, 10);
            updateFuse.stop();
            if(!selection[courseID])
                selection[courseID] = [];
            if($.inArray(crn, selection[courseID]) !== -1){
                //$('.tinyspinner').fadeOut({duration: options.animationDuration});
                options.onSaveComplete();
                return;
            }
            selection[courseID].push(crn);
            updateFuse.start();
        },
        remove: function(options){
            var courseID = options.courseID,
                crn = options.crn;
            if(crn === undefined && courseID === undefined){
                console.error('No crn or courseID provided to remove.');
            }
            if(crn === undefined){
                // remove all sections by course
                self.removeCourse(courseID);
                return;
            }
            if(courseID === undefined){
                // we have to find it.
                courseID = self.getCourseIDByCRN(crn);
                if(courseID === undefined)
                    return;
            }
            self.removeSectionByCourseID(courseID, crn);
        },
        removeCourse: function(courseID){
            updateFuse.stop();
            delete selection[String(courseID)];
            updateFuse.start();
        },
        removeSectionByCourseID: function(courseID, crn){
            courseID = String(courseID);
            crn = parseInt(crn, 10);
            if(!selection[courseID]){
                console.log('no sections were selected in course ' + courseID);
                //$('.tinyspinner').fadeOut({duration: animation_duration});
                options.onSaveComplete();
                return;
            }
            updateFuse.stop();
            if($.inArray(crn, selection[courseID]) === -1){
                console.log(crn, 'not in', courseID);
                //$('.tinyspinner').fadeOut({duration: animation_duration});
                options.onSaveComplete();
                return;
            }
            selection[courseID].removeItem(crn);
            if(selection[courseID].length === 0)
                delete selection[courseID];
            updateFuse.start();
        }
    });
}
var animation_duration = 250;
var selection = new SelectedCourses({
    onSaveComplete: function(){
        $('.tinyspinner').fadeOut({duration: animation_duration});
    }
});
window.selection = selection;

// end selection handling

// event handling for #selected
function sectionChanged(evt){
    // update selection via ajax ???
    var crn = $(this).attr('data-crn'), courseID = $(this).attr('data-cid');
    $(this).parents('.course').find('.tinyspinner').fadeIn({duration:animation_duration});

    selection.saveStateForUndo((function($el){
        return function(){
            $el.removeAttr('checked');
        };
    })($(this)));

    if (this.checked){
        selection.add(courseID, crn);
        // check parent if not done so
        $(this).parents('.course').find('input[type=checkbox]:first').attr('checked', 'checked');
        return;
    }

    selection.removeSectionByCourseID(courseID, crn);
}

function courseChanged(evt){
    var $sections = $(this).parent().find('.section input[type=checkbox]');
    if (this.checked)
        $sections.attr('checked', 'checked');
    else
        $sections.removeAttr('checked');

    selection.saveStateForUndo((function($el){
        return function(){
            $el.removeAttr('checked');
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
        selection.add(courseID, this);
    });

    if(availableCrns.length === 0){
        $('.tinyspinner').fadeOut({duration: animation_duration});
    }
}

function removeFromSelected($course){
    var courseID = $course.attr('data-cid'),
        crns = Utils.splitNonEmpty($course.attr('data-crns'));

    $.each(crns, function(){
        selection.removeSectionByCourseID(courseID, this);
    });
}
// end selection GUI modifiers

// event handling for #courses
function courseSelected(evt){
    var el = evt.target, $el = $(el);
    if (!$el.is('input[type=checkbox]') || $el.parent('.section').length)
        return;

    selection.saveStateForUndo((function($el){
        return function(){
            $el.removeAttr('checked');
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

    selection.fetch();
});

})(jQuery, window, document);
