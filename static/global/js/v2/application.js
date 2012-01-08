// require: objects.js
(function($, window, document, undefined){

///////////////////////////////////////////////////
// functions
var integer = function(i){ return parseInt(i, 10); };
var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
var CSRFToken = function(){
  return getCookie('csrftoken');
};

///////////////////////////////////////////////////
// global hooks

// modify ajax requests to use csrf token for local POST requests
// taken from https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
$(document).ajaxSend(function(event, xhr, settings) {
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", CSRFToken());
    }
});

///////////////////////////////////////////////////
// User Interface

// realtime search initialization
$(function(){
	var defaultHtml = $('#replacable-with-search').html();
	var searchElement = $('#searchform');
	if(searchElement.length){
		var SearchForm = new RealtimeForm(searchElement, {
			updateElement: '#replacable-with-search',
			additionalGET: {partial: 1},
			activityIndicatorElement: '#search-spinner',
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

var Conflicts = Class.extend({
  init: function(){
    this.sections = {};
  },
  add: function(section, section1){
    if (this.has(section)
      this.sections[section] = [];
    this.sections[section].push(section1);
  },
  set: function(section, conflicts){
    this.sections[section] = conflicts;
  },
  get: function(section){
    return this.sections[section];
  },
  has: function(section){
    return typeof this.sections[section] === 'undefined';
  },
  update: function(){
  },
  // fetches data from the server
  sync: function(){
  }
});

var Selected = Class.extend({
  options: {
    course_id_format: 'selected_course_{{ cid }}',
    section_id_format: 'selected_course_{{ cid }}_{{ crn }}',
    checkbox_selector: '.course input[type=checkbox]'
  },
  init: function(options){
    this.course_ids = [];
    this.crns = {};
    this.options = $.extend({}, this.options, options);
  },
  // returns object of course data
  _processCourseElement: function(el){
    var $el = $(el);
    return {
      id: integer($el.attr('data-cid')),
      CRNs: $el.attr('data-crns').split(',').filter(String.prototype.isBlank).map(integer),
      fullCRNs: $el.attr('data-crns-full').split(',').filter(String.prototype.isBlank).map(integer)
    };
  },
  // returns an object for section data
  _processSectionElement: function(el){
    var $el = $(el);
    return {
      course_id: integer($el.attr('data-cid')),
      crn: integer($el.attr('data-crn'))
    };
  },
  _trigger: function(names, obj){
    var $self = $(this);
    for(var i=0, l=names.length; i<l; i++){
      $self.trigger(names[i], obj);
    }
  },
  _isCourseElement: function(el){
    return $(el).attr('data-crns-full') !== undefined;
  },
  _add: function(course_id, crn){
    this.crns[course_id] || (this.crns[course_id] = []);
    if (!this.crns[course_id].pushUnique(crn)) return false;
    this.course_ids.pushUnique(course_id);
    this._trigger(['changed', 'changed:item'], {type: 'added', cid: course_id, crn: crn});
    return true;
  },
  addCourse: function(course_elem){
    var obj = this._processCourseElement(course_elem),
      crns = obj.CRNs.excludeFrom(obj.fullCRNs),
      added = false;
    for (var i=0, l=crns.length; i<l; i++)
      added = this._add(obj.id, crns[i]) || added;
    // if none were added (because all were full), explicitly add all sections
    if (!added){
      for (var i=0, l=obj.CRNs.length; i<l; i++)
        this._add(obj.id, obj.CRNs[i]);
    }
    this._trigger(['added', 'added:course'], {type: 'course', cid: obj.course_id});
  },
  addSection: function(section_elem){
    var obj = this._processSectionElement(section_elem);
    this._add(obj.course_id, obj.crn);
    this._trigger(['added', 'added:section'], {type: 'section', cid: obj.course_id, crn: obj.crn});
  },
  add: function(course_or_section_elem){
    if (this._isCourseElement(course_or_section_elem))
      this.addCourse(course_or_section_elem);
    else
      this.addSection(course_or_section_elem);
  },
  _remove: function(course_id, crn){
    if (!(this.crns[course_id] && this.crns[course_id].removeItem(crn))) return;
    this._trigger(['changed', 'changed:item'], {type: 'removed', cid: course_id, crn: crn});
  },
  removeCourse: function(course_elem){
    var obj = this._processCourseElement(course_elem);
    for (var i=0, l=obj.CRNs.length; i<l; i++)
      this._remove(obj.id, obj.CRNs[i]);
    this._trigger(['removed', 'removed:course'], {type: 'course', cid: obj.course_id});
  },
  removeSection: function(section_elem){
    var obj = this._processSectionElement(section_elem);
    this._remove(obj.course_id, obj.crn);
    this._trigger(['removed', 'removed:section'], {type: 'section', cid: obj.course_id, crn: obj.crn});
  },
  remove: function(course_or_section_elem){
    if (this._isCourseElement(course_or_section_elem))
      this.removeCourse(course_or_section_elem);
    else
      this.removeSection(course_or_section_elem);
  },
  _getQueryString: function(){
    var parameters = {}, self = this;
    $.each(this.crns, function(cid, crns){
      parameters[self.options.course_id_format.format({cid: cid})] = "checked";
      $.each(crns, function(i, crn){
        parameters[self.options.section_id_format.format({cid: cid, crn: crn})] = "checked";
      });
    });
    return $.param(parameters);
  },
  update: function(){
    // write crns to server
    var self = this, $el = $('#courses form');
    self.request = $.ajax({
      url: $el.attr('data-set-url'),
      type: $el.attr('method'),
      data: this._getQueryString(),
      dataType: 'text',
      cache: false,
      success: function(response){
        var json = $.parseJSON(response.substring('for(;;);'.length));
        console.log('success', arguments, json);
        self.crns = json;
        self._trigger(['changed', 'changed:update'], self, self.crns);
      },
      error: function(xhr, status){
        console.log('error', arguments);
      },
      complete: function(){
      }
    });
  },
  set: function(selected_courses){
    this.crns = selected_courses;
    this.course_ids = [];
    for (var prop in this.crns){
      if (this.crns.hasOwnProperty(prop)){
        this.course_ids.push(integer(prop));
      }
    }
    console.log('set', this.crns, this.course_ids);
    return this;
  },
  _getCourseElem: function(course_id){
    return $('#' + this.options.course_id_format.format({cid: course_id}));
  },
  _getSectionElem: function(course_id, crn){
    return $('#' + this.options.section_id_format.format({cid: course_id, crn: crn}));
  },
  refresh: function(){
    // update DOM to reflect selection
    $(this.options.checkbox_selector).checked(false); // this can be a bottleneck if there's enough elements
    var self = this;
    $.each(this.course_ids, function(i, cid){
      var crns = self.crns[cid];
      if (crns && crns.length){
        var $course = self._getCourseElem(cid).checked(true);
        $.each(self.crns[cid], function(i, crn){
          self._getSectionElem(cid, crn).checked(true);
        });
      }
    });
  }
});

//  Selected Course Feature
var selected = new Selected();
$(function(){
  $('#courses .course > input[type=checkbox], #courses .course .section > input[type=checkbox]').bind('change', function(){
    //(this.checked ? selected.add : selected.remove)(this);
    (this.checked ? selected.add(this) : selected.remove(this));
  });
  // automatically refresh after any changes
  var sync = function(){
    selected.refresh();
    selected.update();
  }
  $(selected).bind('added', sync).bind('removed', sync);
});

// public interface
window.Scheduler = {
  Selected: Selected,
  selection: selected
};

})(jQuery, window, document);
