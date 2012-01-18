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
  $('#courses .course > input[type=checkbox], #courses .course .section > input[type=checkbox]').bind('change', function(){
    //(this.checked ? selected.add : selected.remove)(this);
    (this.checked ? Scheduler.selection.add(this) : Scheduler.selection.remove(this));
    Scheduler.selection.save();
  });
  // automatically refresh after any changes
  var refresh = function(){
    Scheduler.selection.refresh();
  };
  $(Scheduler.selection).bind('added', refresh).bind('removed', refresh);
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

  console.log(Scheduler.selection.crns);
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
