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
  start: function(url){
    var self = this;
    $(this.options.bindEventTo).bind('popstate', function(){
      self.load();
    });
  },
  load: function(url){
    url = url || location.pathname;
    var args = this.parse_schedules_url(url);
    this.load_schedules.apply(this, args);
  },
  parse_schedules_url: function(url){
    var parts = url.split('/');
    return [parts[2], parts[3], parts[5]];
  },
  build_schedules_url: function(year, month, slug){
    var url = Scheduler.getURL().replace(/\?.+$/, '');
    if (slug)
      url += '?slug=' + slug;
    return url;
  },
  load_schedules: function(year, month, slug, replaceState){
    var target = $('#schedules');
    var thumbnailsContainer = $('#thumbnails').hide();
    var self = this;

    Scheduler.thumbnails = [];
    $.ajax(Scheduler.getURL(), {
      type: 'GET',
      dataType: 'json',
      success: function(json){
        if(json.schedules && json.schedules.length){
          var url = '/semesters/' + year + '/' + month + '/schedules/';
          if (json.selection_slug) url += json.selection_slug + '/';

          self.mark(url, replaceState);

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
          Scheduler.thumbnails[0].selectSchedule();

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
  // if we're pointed to a schedule... disable all saving features
  var isReadOnly = $('#courses').attr('data-readonly');
  if (!isReadOnly){
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
  }

  // must be on selected courses page
  if(!$('#selected_courses').length) return;

  // load alternative schedule
  var schedule = $('#courses').attr('data-selection');
  if (schedule){
    Scheduler.selection = new Selection({
      store: new MemoryStore(),
      autoload: false
    }).set($.parseJSON($('#courses').attr('data-raw-selection')));
  }

  Scheduler.courseListView = new CourseListView({
    el: '#selected_courses',
    course_ids: Scheduler.selection.getCourseIds(),
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
  Scheduler.state = new Scheduler.State({root: window.location.pathname});
  Scheduler.state.start(Scheduler.getURL());
});
