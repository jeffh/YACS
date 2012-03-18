// require: objects.js
var Scheduler = {};
Scheduler.selection = new Selection();

///////////////////////////////////////////////////
// Data fetching
function getSavedSelection(){
  var data = $('meta[name=selection-raw]').attr('content');
  var obj = null;
  if($.trim(data) !== '')
    obj = $.parseJSON(data);
  return obj;
}

///////////////////////////////////////////////////
// Hooks

// realtime search
$(function(){
  var searchElement = $('#searchform');
  if(searchElement.length){
    var defaultHtml = $('#replacable-with-search').html();
    searchElement.submit(function(){ return false; });
    var SearchForm = new RealtimeForm(searchElement, {
      cache: true,
      updateElement: '#replacable-with-search',
      additionalGET: {partial: 1},
      triggerDelay: 300,
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
        query = form.find('#q').val();
        if($.trim(query) === ''){
          $('#replacable-with-search').html(defaultHtml);
          Scheduler.selection.refresh();
          return true;
        }
        fuse();
        return false;
      },
      success: function(value){
        $('#replacable-with-search').html(value);
        Scheduler.selection.refresh();
      }
    });
  }
});

//  Selected Course Feature
$(function(){
  // if we're pointed to a schedule... disable all saving features
  var isReadOnly = $('#courses').attr('data-readonly');
  // async saves makes the click feel faster
  var saveFuse = DelayedInvocation(function(){ Scheduler.selection.save(); });
  $('#courses .course > input[type=checkbox], #courses .course .section > input[type=checkbox]').live('change', function(){
    (this.checked ? Scheduler.selection.add(this) : Scheduler.selection.remove(this));
    saveFuse();
  });
  // automatically refresh after any changes
  var refresh = function(){
    Scheduler.selection.refresh();
  };
  $(Scheduler.selection).bind('added', refresh).bind('removed', refresh);

  refresh();

  // must be on selected courses page
  if(!$('#selected_courses').length){
    return;
  }

  // load alternative schedule
  var schedule = getSavedSelection();
  if (schedule){
    var selection = new Selection({
      store: new MemoryStore(),
      autoload: false
    }).set(schedule);
    if (_.isEqual(Scheduler.selection.getRaw(), selection.getRaw())){
      $('#courses input[type=checkbox]').removeAttr('disabled');
      isReadOnly = false;
      log(['equal!']);
      // we're equal -- don't say anything
    } else {
      log(['not equal!', Scheduler.selection.getRaw(), selection.getRaw()], this);
      $('#notifications').fadeIn(1000);
      Scheduler.selection = selection;
      $('a[data-action=adopt-selection]').bind('click', function(){
        Scheduler.selection = new Selection().set(schedule);
        Scheduler.selection.save();
        // it's easier to just reload the page (letting the link follow through)
        var spinner = $($('img.spinner').get(0)).clone().css({display: 'inline'});
        var notifications = $('#notifications');
        notifications.fadeOut(100, function(){
          notifications.html(spinner).width($('.nav').width()).fadeIn(100);
        });
        $(this).unbind();
      });
    }
  }

  Scheduler.courseListView = new CourseListView({
    el: '#selected_courses',
    selected: Scheduler.selection,
    isReadOnly: isReadOnly
  });
});


Scheduler.getURL = function(){
  var schedulesURL = $('#schedules').attr('data-source');
  if(!schedulesURL) return;
  if (schedulesURL.indexOf('&id=') < 0){
    Scheduler.selection.getCRNs().each(function(crn){
      schedulesURL += '&id=' + crn;
    });
  }
  return schedulesURL;
};

// Bootloader for schedules
$(function(){
  if(!$('#schedules').length) return;
  if (!_.isEqual(Scheduler.selection.getRaw(), getSavedSelection()))
    $('#notifications').fadeIn(1000);
  Scheduler.view = new ScheduleRootView({
    baseURL: $('meta[name=schedules-url]').attr('content'),
    section_ids: Scheduler.selection.getCRNs()
  }).render();
});
