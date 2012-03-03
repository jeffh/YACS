// require: objects.js
Scheduler = {};
Scheduler.selection = new Selection();

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


Scheduler.getURL = function(){
  var schedulesURL = $('#schedules').attr('data-source');
  if(!schedulesURL) return;
  Scheduler.selection.getCRNs().each(function(crn){
    schedulesURL += '&crn=' + crn;
  });
  return schedulesURL;
};

// Schedules feature
$(function(){
  if(!$('#schedules').length) return;
  var target = $('#schedules');
  var thumbnailsContainer = $('#thumbnails').hide();

  Scheduler.thumbnails = [];
  $.ajax(Scheduler.getURL(), {
    type: 'GET',
    dataType: 'json',
    success: function(json){
      if(json.schedules && json.schedules.length){
        // primary schedule view
        Scheduler.view = new ScheduleView({
          el: target,
          json: json,
          scheduleIndex: 0,
          thumbnailsContainerEl: thumbnailsContainer
        }).render();

        // thumbnails
        thumbnailsContainer.html('');
        for(var i=0, l=json.schedules.length; i<l; i++){
          var view = new ThumbnailView({
            json: json,
            scheduleIndex: i,
            scheduleView: Scheduler.view
          });
          Scheduler.thumbnails.push(view);
          thumbnailsContainer.append(view.render().el);
        }

        return;
      }
      // ERROR
      Scheduler.view = new NoSchedulesView({el: target}).render();
    },
    error: function(xhr, status){
      // TODO: show a custom error page
      if(xhr.status === 403){
        Scheduler.view = new TooManyCRNsView({el: target}).render();
      } else {
        //alert('Failed to get schedules... (are you connected to the internet?)');
        // TODO: log to the server (if we can)
        console.error('Failed to save to schedules: ' + xhr.status);
      }
    }
  });
  /*
  Scheduler.schedulesListView = new SchedulesListView({
    selection: Scheduler.selection,
    periodHeight: Utils.integer($('#schedule-template').attr('data-period-height')),
    thumbnailPeriodHeight: Utils.integer($('#thumbnail-template').attr('data-period-height'))
  });
  */
  /*
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
  */
});
