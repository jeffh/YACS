// require: objects.js
Scheduler = {};
Scheduler.selection = new Selection();

///////////////////////////////////////////////////
// Routing for schedules view

Scheduler.State = Class.extend({
  options: {
    bindEventTo: window,
    history: window.history,
    root: window.location.pathname
  },
  init: function(options){
    this.options = $.extend({}, this.options, options);
  },
  mark: function(url, replaceState){
    if (replaceState)
      this.options.history.pushState({path: url}, '', url);
    else
      this.options.history.replaceState({path: url}, '', url);
  },
  start: function(){
    var self = this;
    $(this.options.bindEventTo).bind('popstate', function(){
      var index = parseInt($('#schedules').attr('data-start') || 0, 10);
      self.load(location.pathname, index);
    });
  },
  load: function(url, index){
    url = url || location.pathname;
    console.log(url);
    var args = this.parseSchedulesURL(url);
    args.push(index || 0);
    this.loadSchedules.apply(this, args);
  },
  parseSchedulesURL: function(url){
    var parts = url.split('/');
    return [parts[2], parts[3], parts[5]];
  },
  loadSchedules: function(year, month, slug, index, replaceState){
    var target = $('#schedules');
    var thumbnailsContainer = $('#thumbnails').hide();
    var self = this;

    Scheduler.thumbnails = [];
    $.ajax(Scheduler.getURL(), {
      type: 'GET',
      dataType: 'json',
      success: function(json){
        if(json.schedules && json.schedules.length){
          var createURL = function(year, month, slug, index){
            var url = '/semesters/' + year + '/' + month + '/schedules/';
            if (json.selection_slug){
              url += json.selection_slug + '/';
              if (index > 0) url += index + '/';
            }
            return url;
          }
          var loadedURL = createURL(year, month, slug, index);

          // primary schedule view
          Scheduler.view = new ScheduleView({
            el: target,
            json: json,
            scheduleIndex: 0,
            thumbnailsContainerEl: thumbnailsContainer
          }).render();

          $(Scheduler.view).bind('scheduleIndexChanged', function(evt){
            var url = createURL(year, month, slug, evt.index + 1);
            self.mark(url, url === loadedURL);
          });

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
          Scheduler.thumbnails[index].selectSchedule();

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
  }
});

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
          //Scheduler.selection.refresh();
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
  if(!$('#selected_courses').length) return;

  // load alternative schedule
  var schedule = $('#courses').attr('data-selection');
  if (schedule){
    var selection = new Selection({
      store: new MemoryStore(),
      autoload: false
    }).set($.parseJSON($('#courses').attr('data-raw-selection')));
    if (_.isEqual(Scheduler.selection.crns, selection.crns)){
      $('#courses input[type=checkbox]').removeAttr('disabled');
      isReadOnly = false;
      // we're equal -- don't say anything
    } else {
      $('#notifications').fadeIn(1000);
      Scheduler.selection = selection;
      $('a[data-action=adopt-selection]').bind('click', function(){
        Scheduler.selection = new Selection().set($.parseJSON($(this).attr('data-raw-selection')));
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
  if (schedulesURL.indexOf('&crn=') < 0){
    Scheduler.selection.getCRNs().each(function(crn){
      schedulesURL += '&crn=' + crn;
    });
  }
  return schedulesURL;
};

// Bootloader for schedules
$(function(){
  if(!$('#schedules').length) return;
  // TODO: check if current selection already matches or not
  $('#notifications').fadeIn(1000);
  Scheduler.state = new Scheduler.State({root: window.location.pathname});
  Scheduler.state.start();
});
