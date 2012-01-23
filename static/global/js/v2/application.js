// require: objects.js

///////////////////////////////////////////////////
// Hooks

// realtime search initialization
$(function(){
	var defaultHtml = $('#replacable-with-search').html();
	var searchElement = $('#searchform');
	if(searchElement.length){
		var SearchForm = new RealtimeForm(searchElement, {
            cache: true,
			updateElement: '#replacable-with-search',
			additionalGET: {partial: 1},
            activityResponder: new ActivityResponder({
              show: function(){
                $('#search-spinner').show();
              },
              hide: function(){
                $('#search-spinner').hide();
              }
            }),
			suppressFormSubmit: true,
			customHandler: function(form, fuse){
				var dept = form.find('#d').val(),
					query = form.find('#q').val();
				if(query === '' && dept === 'all'){
					$('#replacable-with-search').html(defaultHtml);
					return true;
				}
				fuse.start();
				return false;
			}
		});
	}
});

Scheduler = {};
Scheduler.selection = new Selection();

//  Selected Course Feature
$(function(){
  // async saves makes the click feel faster
  var saveFuse = new Fuse({ trigger: function(){ Scheduler.selection.save(); } });
  $('#courses .course > input[type=checkbox], #courses .course .section > input[type=checkbox]').live('change', function(){
    (this.checked ? Scheduler.selection.add(this) : Scheduler.selection.remove(this));
    saveFuse.start();
  });
  // automatically refresh after any changes
  var refresh = function(){
    Scheduler.selection.refresh();
  };
  $(Scheduler.selection).bind('added', refresh).bind('removed', refresh);

  // must be on selected courses page
  if(!$('#selected_courses').length) return;

  Scheduler.courseListView = new CourseListView({
    el: '#selected_courses',
    course_ids: Scheduler.selection.getCourseIds(),
    selected: Scheduler.selection
  });
});

// Schedules feature
$(function(){
  if(!$('#schedules').length) return;
  $('.schedule_wrapper').hide().filter(':first').show();
  $('#thumbnails').hide();
  var scheduleTemplate = new Template({selector: '#schedule-template'}),
    thumbnailTemplate = new Template({selector: '#thumbnail-template'}),
    noSchedulesTemplate = new Template({selector: '#no-schedules-template'}),
    tooManyCRNsTemplate = new Template({selector: '#too-many-crns-template'});

  Scheduler.UI = new ScheduleUI({
    selection: Scheduler.selection.crns,
    schedulesURL: $('#schedules').attr('data-source'),
    scheduleTemplate: scheduleTemplate,
    thumbnailTemplate: thumbnailTemplate,
    noSchedulesTemplate: noSchedulesTemplate,
    tooManyCRNsTemplate: tooManyCRNsTemplate,
    periodHeight: Utils.integer($('#schedule-template').attr('data-period-height')),
    thumbnailPeriodHeight: Utils.integer($('#thumbnail-template').attr('data-period-height'))
  }).fetchSchedules();
});
