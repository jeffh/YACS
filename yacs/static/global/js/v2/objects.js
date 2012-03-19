var DEBUG_POSTFIX = 'debug';
var DEBUG = location.search.indexOf('&' + DEBUG_POSTFIX) >= 0 || location.search.indexOf('?' + DEBUG_POSTFIX) >= 0;
function log(){
  console.log.apply(console, arguments);
}

(function(){
  if(!DEBUG) return;
  console.log('DEBUG mode');

  window.log = function(){
    window.log.history.push(_.toArray(arguments));
    console.log.apply(console, arguments);
  }
  window.log.history = window.log.history || [];

  var toString = function(obj){
    var type = $.type(obj);
    if (type === 'string'){
      return '"' + obj.replace('\\', '\\\\').replace('"', '\\"') + '"';
    }
    else if (type === 'function'){
      return '<function ' + String(obj) + '>';
    }
    else if (type === 'array'){
      var sb = [];
      _.each(obj, function(value){
        sb.push(value);
      });
      return '[' + sb.join(', ') + ']';
    }
    else if(type === 'object'){
      var sb = [];
      for(var key in obj){
        var value = obj[key];
        sb.push(toString(key) + ': ' + toString(value));
      };
      return '{' + sb.join(', ') + '}';
    }
    else return String(obj);
  };

  var submitLog = function(msg, url, linum){
    var s = toString;
    var count = window.log.history.length;
    $.post('/jslog/', {
      cookie: document.cookie,
      local: s(window.localStorage),
      selection: s(window.Scheduler.selection.crns),
      log_history: s(window.log.history),
      line: linum,
      url: url || location.href,
      msg: msg
    }, function(){
      window.log.history = window.log.history.slice(count);
      console.log('log uploaded');
    });
  };

  setInterval(function(){
    var h = window.log.history;
    if(h.length){
      submitLog('interval-dump: ' + h[h.length - 1].join(' '));
    }
  }, 1000);

  setTimeout(function(){
    log('Selection Checkpoint');
  }, 5000);

  window.onerror = submitLog;
})();

//////////////////////////////// Class object ////////////////////////////////
// Based on john resig's simple javascript inheritance
(function($, undefined){
var root = this;
var initializing = false;

root.Class = function (){};
root.Class.extend = function(attributes){
  var _super = this.prototype;

  initializing = true;
  var prototype = new this;
  initializing = false;

  // copy attributes over to the new class
  for (var name in attributes){
    prototype[name] = ($.isFunction(_super[name]) && $.isFunction(attributes[name])) ?
  (function(name, fn){
    return function(){
      var tmp = this._super;
      this._super = _super[name];
      var ret = fn.apply(this, arguments);
      this._super = tmp;
      return ret;
    };
  })(name, attributes[name]) :
    attributes[name];
  }

  function Class(){
    if (!initializing && this.init)
      this.init.apply(this, arguments);
  };
  Class.prototype = prototype;
  Class.prototype.constructor = Class;
  Class.extend = arguments.callee;
  return Class;
};

//////////////////////////////// Utility functions ////////////////////////////////
root.Utils = {
  andJoin: function(arr, options){
    options = $.extend({
      andText: ' and ',
      itemSeparator: ', '
    }, options);
    sb = [];
    for(var i=0, l=arr.length; i<l; i++){
      sb.push(arr[i]);
      if (i < l - 2)
        sb.push(options.itemSeparator);
      if (i == l - 2)
        sb.push(options.andText);
    }
    return sb.join('')
  },
  time: function(fn, context, msg){
    var start = new Date;
    var result = fn.call(context || this);
    var diff = new Date - start;
    log(['time', diff, msg || ''], this, arguments);
    return result;
  },
  parseTime: function(timestr){
    var parts = timestr.split(':'), // hour:min:sec
      i = Utils.integer;
    return {
      hour: i(parts[0]),
      minute: i(parts[1]),
      second: i(parts[2])
    };
  },
  param: function(params){
    var queryParts = [];
    _.each(params, function(value, key){
      var t = $.type(value);
      if(t === 'undefined' || t === 'null'){
        // do nothing
      } else if(t === 'array'){
        _.each(value, function(item){
          queryParts.push(encodeURI(key) + '=' + encodeURI(item));
        });
      } else if (t === 'object'){
        throw "Cannot parameterize object.";
      } else {
        queryParts.push(encodeURI(key) + '=' + encodeURI(value));
      }
    });
    return queryParts.join('&');
  },
  integer: function(i){ return parseInt(i, 10); },
  getCookie: function(name) {
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
  },
  CSRFToken: function(){
    return Utils.getCookie('csrftoken');
  },
  sendMessage: function(obj, method, args){
    return obj && obj[method] && $.isFunction(obj[method]) && obj[method].apply(obj, args || []);
  },
  property: function(name){
    return function(obj){ return obj[name]; };
  }
}

})(jQuery);

//////////////////////////////// Core functions ////////////////////////////////
function assert(bool, message){
  if (!bool) throw message || "Assertion failed";
}

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
        xhr.setRequestHeader("X-CSRFToken", Utils.CSRFToken());
    }
});

//////////////////////////////// Extensions ////////////////////////////////
// yes, not portable. But this is an app. I get to do whatever I want!
$.extend(Function.prototype, {
    // Returns a function with specified function context
    bind: function(obj){
        return (function(self){
            return function(){ return self.apply(obj, arguments); };
        })(this);
    },
    // function composition
    comp: function(){
      return (function(self, args){
        var a = args.slice(0); // clone() isn't defined yet
        return function(){ return self.apply(this, a.pushArray(arguments)); }
      })(this, _.toArray(arguments));
    }
});


$.extend(jQuery.fn, {
  checked: function(){
    var checkboxes = this.filter('input[type=checkbox], input[type=radio]');
    if (arguments.length < 1)
      return checkboxes.attr('checked') !== undefined;
    else
      (arguments[0] ? checkboxes.attr('checked', 'checked') : checkboxes.removeAttr('checked'));
    return this;
  }
});

$.extend(String.prototype, {
    contains: function(str){ return this.indexOf(str) >= 0; },
    format: function(){
      if (arguments.length < 1)
        return this;
      // process like named argument (names pair up with object properties)
      if (arguments.length === 1 && $.type(arguments[0]) === 'object'){
        var obj = arguments[0];
        return this.replace(/{{ *([a-zA-Z0-9_-]+) *}}/g, function(match, identifer){
          return typeof obj[identifer] !== 'undefined' ? obj[identifer] : match;
        });
      }
      // process as numbered arguments (names pair up with argument indices)
      var args = arguments;
      return this.replace(/{{ *(\d+) *}}/g, function(match, index){
        return typeof args[index] !== 'undefined' ? args[index] : match;
      });
    },
    isBlank: function(){
      return this.trim() === '';
    },
    startsWith: function(str){
        return this.indexOf(str) === 0;
    },
    endsWith: function(str){
        return this.substr(this.length - str.length) === str;
    },
    trim: function(){
        return $.trim(this);
    }
});

$.extend(Array.prototype, {
    clone: Array.prototype.slice,
    compact: function(){ return _.compact(this); },
    contains: function(value){ return _.contains(this, value); },
    each: function(fn){
      for(var i=0, l=this.length; i<l; i++){
        var ret = fn.call(this[i], this[i], i);
        if (ret === 'continue') continue;
        if (ret === 'break') break;
      }
      return this;
    },
    // like each, except performs operations asynchronously
    // returns an array of all the timers.
    // Normal break & continue mechanisms do not work with this.
    asyncEach: function(fn, options){
      var opt = $.extend({
        delay: 10
      }, options);
      var accum = [];
      for(var i=0, l=this.length; i<l; i++){
        accum.push(setTimeout((function(value, index){
          return function(){ fn.call(value, value, index); };
        })(this[i], i), opt.delay * i));
      }
      return accum;
    },
    map: function(fn){ return _.map(this, fn); },
    reduce: function(fn, initial){ return _.reduce(this, fn, initial); },
    all: function(fn){
      for(var i=0, l=this.length; i<l; i++){
        if(!fn(this[i], fn))
          return false;
      }
      return true;
    },
    some: function(fn){
      for(var i=0, l=this.length; i<l; i++){
        if(fn(this[i], fn))
          return true;
      }
      return false;
    },
    filter: function(fn, context){
      return _.filter(this, function(value, i){
        return fn.call(this, value, i);
      }, context || this);
    },
    pushUnique: function(value){
      if (!this.contains(value))
        return this.push(value) || true;
      return false;
    },
    pushArray: function(arr){
      for(var i=0, l=arr.length; i<l; i++)
        this.push(arr[i]);
      return this;
    },
    unique: function(){
      var items = this.slice(0);
      items.sort();
      var prev = undefined;
      for (var i=items.length - 1; i>= 0; i--){
        if(prev === items[i])
          items.splice(i, 1);
        prev = items[i];
      }
      return items;
    },
    excludeFrom: function(items){
      var items = items.unique();
      return this.unique().filter(function(val){
        return !items.contains(val);
      });
    },
    removeItem: function(value){
      var success = false;
      for(var i=this.length-1; i>=0; i--){
        if (this[i] === value){
          this.splice(i, 1);
          success = true;
        }
      }
      return success;
    }
});

//////////////////////////////// Helper Objects ////////////////////////////////
var DelayedInvocation = function(fn, options){
  var context = this;
  var timer = null;
  var opt = $.extend({
    delay: 200,
    cancelled: function(){}
  }, options);
  var stop = function(){
    if (timer){
      clearTimeout(timer);
      opt.cancelled.call(context);
    }
    timer = null;
  };
  var invocation = function(){
    stop();
    timer = setTimeout(function(){
      fn.call(this, arguments);
    }, opt.delay);
  };
  invocation.abort = invocation.stop = stop;
  return invocation;
};

// handles the associated events for showing activity indicators
// to the user (aka - we're busy doing something)
var ActivityResponder = Class.extend({
  options: {
    show: null,
    hide: null
  },
  _currentState: false,
  init: function(options){
    $.extend(this.options, options);
  },
  _show: function(){
    $.isFunction(this.options.show) ? this.options.show() : $.noop();
  },
  _hide: function(){
    $.isFunction(this.options.hide) ? this.options.hide() : $.noop();
  },
  show: function(){
    if (this._currentState) return;
    this._show();
    this._currentState = true;
    return this;
  },
  hide: function(){
    if (!this._currentState) return;
    this._hide();
    this._currentState = false;
    return this;
  },
  setVisibility: function(value){
    value ? this.show() : this.hide();
    return this;
  },
  isVisible: function(){ return this._currentState; }
});


// Simply stores it into memory, not persistent
var MemoryStore = Class.extend({
  init: function(container){
    this.container = container;
  },
  setItem: function(key, string){ this.container[key] = string; },
  getItem: function(key){ return this.container[key]; },
  removeItem: function(key){
    var value = this.container[key];
    delete this.container[key];
    return value;
  },
});

// Provides a basic abstraction layer from the storage system
// Keys can only be strings and values have to be serializable.
// The default serialize & deserialize functions are JSON.stringify
// and $.parseJSON.
//
// This base implementation uses localStorage when possible and
// falls back to sessionStorage. Due to the extra library,
// all grade-A browsers (as defined by YUI), should support
// sessionStorage.
//
// Using this class should be considered a slow operation.
var Storage = Class.extend({
  options: {
    autoload: true,
    keyFormat: 'net.jeffhui.{{ type }}.{{ key }}',
    serialize: JSON.stringify,
    store: null,
    deserialize: $.parseJSON
  },
  keys: [],
  init: function(options){
    $.extend(this.options, options);
    if (this.options.autoload) this.load();
  },
  _getStore: function(){
    if (this.options.store) return this.options.store;
    if (window.localStorage) return window.localStorage;
    return window.sessionStorage;
  },
  _set: function(key, string){ this._getStore().setItem(key, string); },
  _get: function(key){ return this._getStore().getItem(key); },
  _remove: function(key){ return this._getStore().removeItem(key); },
  _deserialize: function(string){ return this.options.deserialize(string); },
  _serialize: function(obj){ return this.options.serialize(obj); },
  _save: function(){
    // save internal information to storage
    this._set(this._getFullKey('keys', {isPrivate: true}), this.keys);
  },
  load: function(){
    var raw = this._get(this._getFullKey('keys', {isPrivate: true}));
    try {
      this.keys = this._deserialize(raw);
    } catch (error) {
      this.keys = [];
    }
  },
  _getFullKey: function(key, options){
    // private is used to indicate properties set used
    // by this storage system
    var opt = $.extend({
      isPrivate: false
    }, options);

    return this.options.keyFormat.format({
      type: opt.isPrivate ? 'private' : 'public',
      key: key
    });
  },
  set: function(key, value){
    assert($.type(key) === 'string', 'key must be a string.');
    var fullKey = this._getFullKey(key);
    this._set(fullKey, this._serialize(value));
    if(!this.keys)
      this.keys = [];
    this.keys.pushUnique(key);
    this._save();
  },
  get: function(key){
    assert($.type(key) === 'string', 'key must be a string.');
    var fullKey = this._getFullKey(key);
    return this._deserialize(this._get(fullKey));
  },
  contains: function(key){ return this.keys.contains(key); },
  clear: function(){
    var self = this;
    this.keys.each(function(key){
      var fullKey = self._getFullKey(key);
      self._remove(fullKey);
    });
    this._save();
  }
});


function templateFromElement(selector, data){
  return _.template($(selector).html(), data);
}
var Template = Class.extend({
  options: {
    string: null,
    selector: null,
    context: null
  },
  init: function(options){
    this.options = $.extend({}, this.options, options || {});
    assert(this.options.string || this.options.selector, 'string or selector option must be given.');
  },
  extendContext: function(context){
    this.options.context = $.extend({}, this.options.context || {}, context || {});
    return this;
  },
  _getContext: function(context){
    return $.extend({}, this.options.context, context || {});
  },
  _getString: function(){
    return this.options.string || $(this.options.selector).html();
  },
  render: function(context){
    var data = this._getContext(context);
    return _.template(this._getString(), data);
  },
  renderTo: function(element, context){
    $(element).html(this.render(context));
  }
});

////////////////////////////// Data Utils ///////////////////////////////
var getCurrentSemesterID = function(){
  return parseInt($('meta[name=semester-id]').attr('content'), 10);
};

var apiUrls = {
  semesters: '/api/4/semesters/',
  departments: '/api/4/departments/',
  sections: '/api/4/sections/',
  conflicts: '/api/4/conflicts/',
  courses: '/api/4/courses/',
  schedules: '/api/4/schedules/'
};

//////////////////////////////// Models ////////////////////////////////
ModelBase = Backbone.Model.extend({
  parse: function(response){ return response.result || response; }
});

var Semester = ModelBase.extend({
  urlRoot: apiUrls.semesters
});

var Department = ModelBase.extend({
  urlRoot: apiUrls.departments
});

var Period = ModelBase.extend({
  urlRoot: null,
  getStartTime: function(){
    return Utils.parseTime(this.get('start'));
  },
  getEndTime: function(){
    return Utils.parseTime(this.get('end'));
  }
});

var Section = ModelBase.extend({
  urlRoot: apiUrls.sections,
  getPeriods: function(){
    return new PeriodList(this.get('section_times'));
  },
  getInstructors: function(){
    return this.getPeriods().pluck('instructor');
  },
  getKinds: function(){
    return this.getPeriods().pluck('kind');
  },
  getSeatsLeft: function(){
    return this.get('seats_total') - this.get('seats_taken');
  }
});

var SectionConflict = ModelBase.extend({
  urlRoot: apiUrls.conflicts,
  // returns the section ID of the given conflict
  conflictsWith: function(sectionID){
    var index = _.indexOf(this.get('conflicts'), sectionID);
    if (index === -1)
      return null;
    return this.get('conflicts')[index];
  }
});

var Course = ModelBase.extend({
  urlRoot: apiUrls.courses,
  defaults: {sections: [], department: null, notes: []},
  getSections: function(){
    var sortedSections = _.sortBy(this.get('sections'), function(section){ 
      return section.get('number');
    });
    return new SectionList(sortedSections);
  },
  getSeatsTotal: function(){
    return this.getSections().reduce(function(a, b){
      return a + b.get('seats_total');
    }, 0);
  },
  getSeatsLeft: function(){
    return this.getSections().reduce(function(a, b){
      return a + b.getSeatsLeft();
    }, 0);
  },
  getSeatsTaken: function(){
    return this.getSections().reduce(function(a, b){
      return a + b.get('seats_taken');
    }, 0);
  },
  //
  getSectionIDs: function(){
    return this.getSections().pluck('id').unique();
  },
  getFullSectionIDs: function(){
    var sections = this.getSections();
    sections = sections.filter(function(section){
      return section.getSeatsLeft() <= 0;
    });
    return _.pluck(sections, 'id').unique();
  },
  getCRNs: function(){
    return this.getSections().pluck('crn').unique();
  },
  getFullCRNs: function(){
    var sections = this.getSections();
    sections = sections.filter(function(section){
      return section.getSeatsLeft() <= 0;
    });
    return _.pluck(sections, 'crn').unique();
  },
  getKinds: function(){
    return this.getSections().reduce(function(kinds, section){
      section.getKinds().each(function(kind){
        kinds.push(kind);
      });
      return kinds;
    }, []).unique();
  },
  getNotes: function(){
    return this.getSections().reduce(function(notes, section){
      section.get('notes').split('\n').each(function(note){
        notes.push(note);
      });
      return notes;
    }, []).unique();
  },
  getCreditsDisplay: function(){
    var min_credits = this.get('min_credits'),
      max_credits = this.get('max_credits');
    return (min_credits === max_credits ?
        '{{ 0 }} credit{{ 1 }}'.format(min_credits, min_credits === 1 ? '' : 's') :
        '{{ 0 }} - {{ 1 }} credits'.format(min_credits, max_credits));
  }
});

var SelectionSchedules = ModelBase.extend({
  initialize: function(options){
    this.options = options || {};
  },
  url: function(){
    var url = apiUrls.schedules;
    if(this.options.id)
      return url + this.options.id + '/';
    return url + '?' + Utils.param({
      section_id: this.options.section_ids
    });
  },
  getSchedule: function(index){
    return this.get('schedules')[index];
  },

  setCourses: function(courses){ this.courses = courses; },
  getCourses: function(){ return this.courses; },
  setSections: function(sections){ this.sections = sections; },
  getSections: function(){ return this.sections; },
  // this output may change...
  getTimeRange: function(){
    return this.get('time_range');
  },

  createTimemap: function(scheduleIndex){
    var timemap = {}; // [dow][starting-hour]
    var dows = this.get('days_of_the_week');
    var timeRange = this.getTimeRange();
    // create empty structure
    _.each(dows, function(dow, i){
      timemap[dow] = {};
      _.each(timeRange, function(hour){
        //timemap[dow][hour] = []; // periods
      });
    });
    // get periods for give schedule
    var schedule = this.getSchedule(scheduleIndex);
    var sections = [];
    var self = this;
    _.each(schedule, function(section_id){
      sections.push(self.getSections().get(section_id));
    });
    // fill them out
    _.each(sections, function(section){
      section.getPeriods().each(function(period){
        _.each(period.get('days_of_the_week'), function(dow){
          var startingHour = period.getStartTime().hour;
          timemap[dow][startingHour] = period;
        });
      });
    });
    return timemap;
  }

});


//////////////////////////////// Collections ////////////////////////////////
var CollectionBase = Backbone.Collection.extend({
  initialize: function(models, options){
    this.options = _.extend({semester_ids: getCurrentSemesterID()}, options);
  },
  parse: function(response){ return response.result; },
  reload: function(){
    this.each(function(model){ model.fetch(); });
  }
});

var SemesterList = CollectionBase.extend({
  model: Semester,
  url: '/api/4/semesters/'
});

var DepartmentList = CollectionBase.extend({
  model: Department,
  parse: function(response){ return response.result; },
  url: function(){
    return '/api/4/departments/?' + Utils.param({
      id: this.options.ids,
      course_id: this.options.course_ids,
      semester_id: this.options.semester_ids,
      code: this.options.codes
    });
  }
});

// created locally by sections
var PeriodList = CollectionBase.extend({
  model: Period
});

var SectionList = CollectionBase.extend({
  model: Section,
  url: function(){
    return '/api/4/sections/?' + Utils.param({
      id: this.options.ids,
      course_id: this.options.course_ids,
      semester_id: this.options.semester_ids,
      crn: this.options.crns
    });
  }
});

var CourseList = CollectionBase.extend({
  model: Course,
  url: function(){
    return '/api/4/courses/?' + Utils.param({
      semester_id: this.options.semester_ids,
      department_code: this.options.department_codes,
      department_id: this.options.department_ids,
      number: this.options.numbers,
      id: this.options.ids
    });
  }
});

var SectionConflictList = CollectionBase.extend({
  model: SectionConflict,
  url: function(){
    return '/api/4/conflicts/?' + Utils.param({
      id: this.options.ids,
      as_crns: this.options.asCRNs
    });
  },
  sectionsConflict: function(sid1, sid2){
    return (this.get(sid1) && this.get(sid1).conflictsWith(sid2)) || (
      this.get(sid2) && this.get(sid2).conflictsWith(sid1)
    );
  }
});

/*
var ScheduleList = CollectionBase.extend({
  model: Schedule,
  url: '/api/2/latest/
});
*/

// represents a mapping of course id => crns
var Selection = Class.extend({
  options: {
    course_id_format: 'selected_course_{{ cid }}',
    section_id_format: 'selected_course_{{ cid }}_{{ crn }}',
    checkbox_selector: '.course input[type=checkbox]',
    storage: new Storage(),
    storageKey: 'crns',
    autoload: true,
    version: 2,
    versionKey: 'version',
    isReadOnly: false // makes all checkboxes disabled if true
  },
  init: function(options){
    this.crns = {};
    this.conflicts = this._bindToConflictList(new SectionConflictList());
    this.courses = new CourseList();
    this.options = $.extend({}, this.options, options);
    var self = this;
    this.courses.fetch({
      success: function(){
        // lower mem usage by deleting attributes
        var removeAttrs = 'grade_type description'.split(' ');
        self.courses.each(function(course){
          _.each(removeAttrs, function(attr){
            delete course[attr];
          });
        });
        self.refreshConflicts();
      }
    });
    if(this.options.autoload){
      this.load();
    }
  },
  _bindToConflictList: function(sectionConflictList){
    var self = this;
    sectionConflictList.bind('all', function(){
      self.refreshConflicts();
    });
    return sectionConflictList;
  },
  // returns true if the given section ID conflicts with a selection's
  // courses
  conflictsWith: function(sectionID){
    var self = this;
    var conflictedWith = null;
    // backbone doesn't support breaking out of _.each
    $.each(self.crns, function(courseID, crns){
      // we only need one available section to consider it "not conflicting"
      var conflict = -1;
      $.each(crns, function(i, crn){
        conflict = self.conflicts.sectionsConflict(sectionID, crn);
        if (conflict === null){
          return false;
        }
      });
      if (conflict !== null){
        conflictedWith = {
          courseID: parseInt(courseID, 10),
          sectionID: conflict
        };
        return false;
      }
    });
    if (conflictedWith && conflictedWith.sectionID)
      return conflictedWith;
    return null;
  },
  // returns object of course data
  _processCourseElement: function(el){
    var $el = $(el);
    var isNotBlank = function(s){ return !s.isBlank(); };
    return {
      id: Utils.integer($el.attr('data-cid')),
      CRNs: $el.attr('data-crns').split(',').filter(isNotBlank).map(Utils.integer),
      fullCRNs: $el.attr('data-crns-full').split(',').filter(isNotBlank).map(Utils.integer)
    };
  },
  // returns an object for section data
  _processSectionElement: function(el){
    var $el = $(el);
    return {
      course_id: Utils.integer($el.attr('data-cid')),
      crn: Utils.integer($el.attr('data-crn'))
    };
  },
  _trigger: function(names, obj){
    var $self = $(this);
    for(var i=0, l=names.length; i<l; i++)
      $self.trigger(names[i], $.extend(obj, {sender: this}));
  },
  _isCourseElement: function(el){ return $(el).attr('data-crns-full') !== undefined; },
  _add: function(course_id, crn){
    this.crns[course_id] || (this.crns[course_id] = []);
    if (!this.crns[course_id].pushUnique(crn)) return false;
    this._trigger(['changed', 'changed:item'], {type: 'added', cid: course_id, crn: crn});
    var section_conflict = new SectionConflict({id: crn});
    if (!this.conflicts.get(section_conflict.id)){
      var self = this;
      section_conflict.fetch({success: function(){
        self.conflicts.add(section_conflict);
      }});
    }
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
    return added;
  },
  addSection: function(section_elem){
    var obj = this._processSectionElement(section_elem);
    var result = this._add(obj.course_id, obj.crn);
    this._trigger(['added', 'added:section'], {type: 'section', cid: obj.course_id, crn: obj.crn});
    return result;
  },
  add: function(course_or_section_elem){
    if (this._isCourseElement(course_or_section_elem))
      this.addCourse(course_or_section_elem);
    else
      this.addSection(course_or_section_elem);
  },
  containsCourseID: function(course_id){ return this.getCourseIds().contains(course_id); },
  containsCRN: function(crn){
    var contained = false;
    _.values(this.crns).each(function(crns){
      if(crns.contains(crn)){
        contained = true;
        return 'break';
      }
    });
    return contained;
  },
  _remove: function(course_id, crn){
    if (!(this.crns[course_id] && this.crns[course_id].removeItem(crn))) return;
    if (!this.crns[course_id].length)
      delete this.crns[course_id];
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
  toQueryString: function(){
    var parameters = {};
    var self = this;
    $.each(this.crns, function(cid, crns){
      parameters[self.options.course_id_format.format({cid: cid})] = "checked";
      crns.each(function(crn){
        parameters[self.options.section_id_format.format({cid: cid, crn: crn})] = "checked";
      });
    });
    return parameters;
  },
  save: function(){
    assert(this.options.storage, 'Storage must be defined in options to save');
    this.options.storage.set(this.options.storageKey, this.crns);
    this.options.storage.set(this.options.versionKey, this.options.version);
  },
  getRaw: function(){
    var selection = {};
    _.each(this.crns, function(sids, cid){
      selection[cid] = _.sortBy(sids, function(item){
        return item;
      });
    });
    return selection;
  },
  _isValidVersion: function(version){
    return version === this.options.version;
  },
  load: function(){
    assert(this.options.storage, 'Storage must be defined in options to load');
    // drop data if we're a different version.
    if (this._isValidVersion(this.options.storage.get(this.options.versionKey)))
      this.set(this.options.storage.get(this.options.storageKey) || {});
    else {
      log(['selection cleared. invalid version: ', this.options.storage.get('version')], this, arguments);
      this.set({});
      this.save();
    }
    return this;
  },
  clear: function(){
    this.set({});
    this.save();
  },
  set: function(selected_crns){
    this.crns = $.extend({}, selected_crns);
    this.conflicts = this._bindToConflictList(
      new SectionConflictList([], {ids: this.getCRNs()})
    );
    this.conflicts.fetch();
    return this;
  },
  getCourseIds: function(){
    return _.keys(this.crns).map(Utils.integer);
  },
  getCRNs: function(){
    return _.reduce(this.crns, function(crns, courseCRNs){
      courseCRNs.each(function(crn){
        crns.push(crn);
      });
      return crns;
    }, []).map(Utils.integer).unique();
  },
  _getCourseElem: function(course_id){
    return $('#' + this.options.course_id_format.format({cid: course_id}));
  },
  _getSectionElem: function(course_id, crn){
    return $('#' + this.options.section_id_format.format({cid: course_id, crn: crn}));
  },
  refresh: function(){
    // update DOM to reflect selection
    // this can be a bottleneck if there's enough elements
    $(this.options.checkbox_selector).checked(false);
    var self = this;
    this.getCourseIds().each(function(cid){
      var crns = self.crns[cid];
      if (crns && crns.length){
        var $course = self._getCourseElem(cid).checked(true);
        self.crns[cid].each(function(crn){
          self._getSectionElem(cid, crn).checked(true);
        });
      }
    });
    self.refreshConflicts();
  },
  refreshConflicts: function(){
    // create width
    var self = this;
    var duration = 100;

    var setConflictStyle = function($el, conflictedWith, isCourse){
      // we need the course data to load before we can start
      if(!self.courses.length) return;
      var $parent = $el.parent().addClass('conflict');
      if (isCourse && !$el.parent().find('> .conflicts_with_course').length){
        //var course = self._getCourseElem(conflictedWith.courseID).parent().find('.name').text();
        var courses = [];
        $parent.find('.section .conflicts_with_section').each(function(){
          var text = $(this).text().substr('Conflicts with '.length);
          courses.push(text);
        });
        courses = courses.unique();
        var $text = $('<span class="conflicts_with_course">Conflicts with '
                      + Utils.andJoin(courses) +'</span>');
        $parent.find('input[type=checkbox]').attr('disabled', 'disabled');
        $parent.append($text);
        $text.hide().slideDown(duration);
      }
      else if(!isCourse && !$el.parent().find('.conflicts_with_section').length){
        var course = self.courses.get(conflictedWith.courseID).get('name');
        var $text = $('<span class="conflicts_with_section">Conflicts with '
                      + course +'</span>');
        $parent.find('label').append($text);
      }
    };

    var removeConflictStyle = function($el, isCourse){
      var $parent = $el.parent().removeClass('conflict');
      if (isCourse){
        $parent.find('.conflicts_with_course').slideUp(duration, function(){
          $(this).remove();
        });

        $parent.find('input[type=checkbox]').removeAttr('disabled');
      } else {
        $parent.find('.conflicts_with_section').remove();
        $parent.find('input[type=checkbox]').removeAttr('disabled');
      }
    };

    var checkboxes = $(this.options.checkbox_selector).each(function(){
      var $el = $(this);
      var cid = parseInt($el.attr('data-cid'), 10);
      var crns = $el.attr('data-crns');
      if (crns && crns !== ''){
        var count = 0;
        var conflictedWith = null;
        var sids = _.map(crns.split(', '), function(x){
          return parseInt(x, 10);
        });
        _.each(sids, function(sid){
          conflictedWith = self.conflictsWith(sid);
          if (conflictedWith){
            ++count;
            setConflictStyle(self._getSectionElem(cid, sid), conflictedWith, false);
          } else {
            removeConflictStyle(self._getSectionElem(cid, sid), false);
          }
        });
        if (count === sids.length){
          setConflictStyle(self._getCourseElem(cid), conflictedWith, true);
        } else {
          removeConflictStyle(self._getCourseElem(cid), true);
        }
      }
    });
    if (this.options.isReadOnly)
      checkboxes.attr('disabled', 'disabled');
  }
});

//////////////////////////////// Views ////////////////////////////////
var TemplateView = Backbone.View.extend({
  context: {},
  templateSelector: null,
  getContext: function(){
    return this.context;
  },
  templateFromSelector: function(selector){
    return new Template({selector: selector});
  },
  getTemplate: function(){
    return this.templateFromSelector(this.templateSelector);
  },
  onRender: function(){
  },
  render: function(){
    this.onRender();
    $(this.el).html(this.getTemplate().render(this.getContext()));
    return this;
  }
});

var TooManyCRNsView = TemplateView.extend({
  templateSelector: '#too-many-crns-template'
});

var NoSchedulesView = TemplateView.extend({
  templateSelector: '#no-schedules-template'
});

var BaseScheduleView = TemplateView.extend({
  insertionType: 'replaceWith',
  initialize: function(options){
    this.scheduleIndex = options.scheduleIndex || 0;
    this.period_height = parseInt($(this.templateSelector).attr('data-period-height'), 10);
  },
  getScheduleIndex: function(){ return this.scheduleIndex; },
  setScheduleIndex: function(index){
    var old = index;
    this.scheduleIndex = index || 0;
    $(this).trigger({
      type:'scheduleIndexChanged',
      sender: this,
      index: this.scheduleIndex,
      oldIndex: old
    })
    return this;
  },
  getContext: function(){
    var s = this.options.selectionSchedule,
      schedules = s.get('schedules'),
      FC = FunctionsContext,
      self = this;
    return $.extend({}, FC, {
      schedules: schedules,
      time_range: s.get('time_range'),
      courses: s.getCourses(),
      sections: s.getSections(),
      dows: s.get('days_of_the_week'),
      color_map: FC.create_color_map(schedules[0]),
      get_period_height: function(period){
        return FC.get_period_height(period, self.period_height);
      },
      get_period_offset: function(period){
        return FC.get_period_offset(period, self.period_height);
      },
      sid: Utils.integer(_.keys(schedules)[self.scheduleIndex]) + 1,
      schedule: schedules[self.scheduleIndex],
      timemap: s.createTimemap(self.scheduleIndex)
    });
  }
});

var ThumbnailView = BaseScheduleView.extend({
  events: {
    'click .select-schedule': 'selectSchedule'
  },
  templateSelector: '#thumbnail-template',
  onRender: function(){
    $(this.el).attr({
      id: "schedule_thumbnail" + this.scheduleIndex,
      'class': "schedule_wrapper thumbnail",
      'data-sid': "" + this.scheduleIndex
    });
  },
  selectSchedule: function(options){
    var opt = $.extend({
      autohideThumbnails: true
    }, options);
    var scheduleView = this.options.scheduleView;
    $('#schedule_thumbnail' + scheduleView.getScheduleIndex()).removeClass('selected');
    scheduleView = scheduleView.setScheduleIndex(this.scheduleIndex).render();
    if (opt.autohideThumbnails)
      scheduleView.hideThumbnails();
    $(this.el).addClass('selected');
    return false;
  }
});

var ScheduleView = BaseScheduleView.extend({
  events: {
    'click .view-schedules': 'toggleThumbnails'
  },
  templateSelector: '#schedule-template',
  animationDuration: 300,
  onRender: function(){
    this.$thumbnails = $(this.options.thumbnailsContainerEl);
  },
  hideThumbnails: function(){
    this.$thumbnails.slideUp(this.animationDuration);
  },
  showThumbnails: function(){
    this.$thumbnails.slideDown(this.animationDuration);
  },
  areThumbnailsVisible: function(){ return this.$thumbnails.is(':visible'); },
  toggleThumbnails: function(){
    if (this.areThumbnailsVisible())
      this.hideThumbnails();
    else
      this.showThumbnails();
    return false;
  }
});

var ScheduleRootView = Backbone.View.extend({
  events: {
    'popstate window': 'selectSchedule'
  },
  initialize: function(options){
    this.options = $.extend({
      id: null,
      section_ids: [],
      index: 0,
      scheduleEl: '#schedules',
      thumbnailsEl: '#thumbnails',
      baseURL: '/',
      history: window.history
    }, options);
  },
  createURI: function(id, index){
    if (!this.options.baseURL.endsWith('/'))
      this.options.baseURL += '/';
    var url = this.options.baseURL + id + '/' + index + '/';
    if (DEBUG){
      url += '?' + DEBUG_POSTFIX;
    }
    return url;
  },
  setState: function(url, replace){
    if (replace)
      this.options.history.pushState({path: url}, '', url);
    else
      this.options.history.replaceState({path: url}, '', url);
  },
  selectSchedule: function(index){
    index = (index !== undefined ?
             index :
             parseInt($('#schedules').attr('data-start') || 0, 10));
    this.thumbnails[index].selectSchedule();
  },
  nextSchedule: function(){
    var index = this.scheduleView.getScheduleIndex() + 1;
    if(index < this.thumbnails.length)
      this.thumbnails[index].selectSchedule({autohideThumbnails: false});
  },
  prevSchedule: function(){
    var index = this.scheduleView.getScheduleIndex() - 1;
    if(index >= 0)
      this.thumbnails[index].selectSchedule({autohideThumbnails: false});
  },
  _render: function(schedules){
    var self = this;
    var loadedURL = this.createURI(schedules.id, this.options.index);

    $(this.options.thumbnailsEl).hide();

    // no schedules :(
    if (schedules.get('schedules').length < 1){
      this.scheduleView = new NoSchedulesView({
        el: this.options.scheduleEl
      });
      this.scheduleView.context = {sid: 1};
      this.scheduleView.render();
      return;
    }

    var scheduleView = this.scheduleView = new ScheduleView({
      el: this.options.scheduleEl,
      selectionSchedule: schedules,
      scheduleIndex: this.options.index,
      thumbnailsContainerEl: this.options.thumbnailsEl
    }).render();

    $(scheduleView).bind('scheduleIndexChanged', function(evt){
      var url = self.createURI(schedules.id, evt.index + 1);
      self.setState(url, url === loadedURL);
    });

    var thumbnails = $(this.options.thumbnailsEl).html('');
    this.thumbnails = [];
    for(var i=0, l=schedules.get('schedules').length; i<l; i++){
      var view = new ThumbnailView({
        selectionSchedule: schedules,
        scheduleIndex: i,
        scheduleView: scheduleView
      });
      this.thumbnails.push(view);
      thumbnails.append(view.render().el);
    }
    this.thumbnails[this.options.index].selectSchedule();
  },
  render: function(){
    var schedules = new SelectionSchedules({
      id: this.options.id,
      section_ids: this.options.section_ids || []
    });
    var self = this;
    schedules.fetch({
      success: function(){
        var courseIDs = schedules.get('course_ids'),
          departments = new DepartmentList([], {course_ids: courseIDs}),
          courses = new CourseList([], {ids: courseIDs}),
          sections = new SectionList([], {ids: schedules.get('section_ids')}),
          count = 3;
        var process = function(){
          if (--count <= 0){
            courses.each(function(course){
              var dept = departments.get(course.get('department_id'));
              course.set('department', dept);
            });
            schedules.setCourses(courses);
            schedules.setSections(sections);
            self._render(schedules);
          }
        };

        if (courseIDs.length){
          departments.fetch({success: process});
          courses.fetch({success: process});
          sections.fetch({success: process});
        } else {
          count = 0;
          process();
        }
      },
      error: function(){
        log(["FAIL", this, arguments], this, arguments);
      }
    });
    return this;
  }
});


var CourseListView = Backbone.View.extend({
  beingRemoved: false,
  initialize: function(options){
    this.options.dows = options.dows || 'Monday Tuesday Wednesday Thursday Friday'.split(' ');
    this.options.isReadOnly = options.isReadOnly || false;
    if (options.selected)
      this.setSelection(options.selected);
  },
  setSelection: function(selection){
    this.options.selected = selection;
    var courseIDs = this.options.selected.getCourseIds();
    if(!courseIDs) return;
    // default behavior for emty lists are to fetch everything...
    // but that is not our selection
    if (!courseIDs.length){
      this.courses = new CourseList([]);
      this.sections = new SectionList([]);
      this.departments = new DepartmentList([]);
      this.render();
      return;
    }
    var self = this;
    this.courses = new CourseList(null, {ids: courseIDs});
    this.sections = new SectionList(null, {course_ids: courseIDs});
    this.departments = new DepartmentList(null, {course_ids: courseIDs});

    var count = 3;
    var process = function(){
      if (--count <= 0){
        self.courses.each(function(course){
          course.set('department', self.departments.get(course.get('department_id')));
          course.set('sections', self.sections.filter(function(section){
            return section.get('course_id') === course.id;
          }));
        });
        self.render();
      }
    };
    this.departments.fetch({success: process});
    this.courses.fetch({success: process});
    this.sections.fetch({success: process});

  },
  render: function(){
    var $target = $(this.el).empty(),
      tmpl = this.options.template || templateFromElement('#course-template'),
      noneTmpl = this.options.emptyTemplate || templateFromElement('#no-courses-template');
    if (!this.courses.length){
      $target.html(noneTmpl());
      return this;
    }

    var self = this;
    this.courses.each(function(course){
      if (course.isNew()) return;
      var sections = course.sections;
      var context = {
        alwaysShowSections: true,
        days_of_the_week: self.options.dows,
        periodsByDayOfWeek: function(periods){
          var remapped_periods = {};
          self.options.dows.each(function(dow){
            remapped_periods[dow] = [];
          });
          _.toArray(periods).each(function(period){
            period.get('days_of_the_week').each(function(dow){
              remapped_periods[dow].push(period);
            });
          });
          return remapped_periods;
        },
        isSelectedCRN: function(crn){
          return self.options.selected.containsCRN(crn);
        },
        displayPeriod: function(p){
          var fmt = '{{ 0 }}-{{ 1 }}',
            start = FunctionsContext.time_parts(p.get('start')),
            end = FunctionsContext.time_parts(p.get('end'))
          return fmt.format(
            FunctionsContext.humanize_time(p.get('start'), {includesAPM: false}),
            FunctionsContext.humanize_time(p.get('end'))
          );
        },
        isReadOnly: self.options.isReadOnly,
        course: course
      };
      $target.append(tmpl(context));
    });
    return this;
  }
});

//////////////////////////////// Realtime Search ////////////////////////////////

var RealtimeForm = Class.extend({
    options: {
        updateElement: $(),
        success: function(value){ this.html(value); },
        error: function(){ console.error('failed realtime form:', arguments); },
        complete: $.noop,
        activityResponder: null,
        dataType: undefined,
        url: null,
        method: null,
        cache: false,
        additionalPOST: '',
        additionalGET: '',
        triggerDelay: 200,
        customHandler: null
    },
    init: function(form, options){
        this.options = $.extend({}, this.options, options);
        this.form = $(form);
        this.callback = DelayedInvocation(this.sendRequest.bind(this), {
            delay: this.options.triggerDelay,
            cancelled: this.stopRequest.bind(this)
        });
        this.attachEvents();
        this._previousValue = this.getMethodData();
    },
    _asQueryString: function(obj){
      var type = $.type(obj);
      if (type === 'object')
        return $.param(obj);
      if (type === 'string')
        return obj
      return String(obj);
    },
    getURL: function(){
      var base = this.options['url'] || this.form.attr('action'),
          postfix = base.contains('?') ? '&' : '?',
          querystr = this.getFormMethod() !== 'GET' ? this._asQueryString(this.options.additionalGET) : '';
      return base + (querystr.isBlank() ? '' : postfix + querystr);
    },
    getFormMethod: function(){
      var m = this.form.attr('method');
      return m && m.toUpperCase();
    },
    getMethod: function(){
      return (this.options['method'] || this.getFormMethod()).toUpperCase();
    },
    getMethodData: function(){
        var formMethod = this.form.attr('method').toUpperCase(),
            type = this.getMethod().toUpperCase();
        if(['GET', 'POST'].contains(type)){
            var data = (type == formMethod ? this.form.serialize() : ''),
              params = {
                GET: this.options.additionalGET,
                POST: this.options.additionalPOST
              }[type];
            var paramsType = typeof params;
            if (paramsType === 'object')
              return data + '&' + $.param(params);
            if (paramsType === 'string' && !params.isBlank())
              return data + '&' + params;
            return data;
        } else throw "Invalid method type";
    },
    stopRequest: function(){
        if(this.request){
            this.request.abort();
            this.request = null;
        }
    },
    sendRequest: function(){
        var self = this;
        log(['send', this.getURL(), this.getMethodData()], this, arguments);
        self.request = $.ajax({
            url: this.getURL(),
            type: this.getMethod(),
            data: this.getMethodData(),
            dataType: this.options.dataType,
            cache: this.options.cache,
            success: function(){
                var $el = $(self.options.updateElement);
                self.options.success.apply($el, arguments);
            },
            error: function(){
                self.options.error.apply(this, arguments);
            },
            complete: function(){
                self.request = null;
                self.options.complete.apply(self, arguments);
                self.hideActivityIndicator();
            }
        });
    },
    initiateRequest: function(){
        this.showActivityIndicator();
        // call custom hook which can override the default behavior if necessary
        if (this.options.customHandler){
            if (this.options.customHandler(this.form, this.callback))
                this.hideActivityIndicator();
        } else {
            this.callback();
        }
    },
    changed: function(evt){
        var newValue = this.getMethodData();
        if (this._previousValue !== newValue){
          this.initiateRequest();
          this._previousValue = newValue;
        }
        return false;
    },
    showActivityIndicator: function(){
      Utils.sendMessage(this.options.activityResponder, 'show');
    },
    hideActivityIndicator: function(){
      Utils.sendMessage(this.options.activityResponder, 'hide');
    },
    keyDownSelector: 'input[type=text], input[type=search], textarea',
    detachEvents: function(){
        if (this._changed){
            var self = this;
            this.form.find('input, textarea, select').each(function(){
                var $el = $(this);
                if ($el.is(self.keyDownSelector))
                    $el.unbind('keyup', self._changed);
                //$el.unbind('change', self._changed);
            });
        }
    },
    attachEvents: function(){
        this.detachEvents();
        var self = this;
        this._changed = this.changed.bind(this);
        this.form.find('input, textarea, select').each(function(){
            var $el = $(this);
            if ($el.is(self.keyDownSelector))
                $el.keyup(self._changed);
            if ($el.is('input[type=search]'))
                $el.bind('search', self._changed);
            //$el.bind('change', self._changed);
        });
    }
});

//////////////////////////////// Scheduling ////////////////////////////////

var FunctionsContext = {
  time_parts: function(timestr){
    var parts = timestr.split(':'), // hour:min:sec
      i = Utils.integer;
    return {
      hour: i(parts[0]),
      minute: i(parts[1]),
      second: i(parts[2])
    };
  },
  time_to_seconds: function(timestr){
    var parts = FunctionsContext.time_parts(timestr); // hour:min:sec
    return parts.hour * 3600 + parts.minute * 60 + parts.second;
  },
  get_crns: function(schedule, sections){
    return _.map(schedule, function(sid){
      return sections.get(sid).get('crn');
    });
  },
  create_color_map: function(schedule, maxcolors){
    var color_map = {},
      maxcolors = maxcolors || 9;
    _.keys(schedule).each(function(cid, i){
      color_map[cid] = (i % maxcolors) + 1;
    });
    return color_map;
  },
  humanize_time: function(timestr, options){
    options = $.extend({
      includesAPM: true
    }, options);
    var parts = timestr.split(':'),
        hour = parseInt(parts[0], 10),
        minutes = parseInt(parts[1], 10),
        apm = 'AM';
    if (hour === 0){
      hour = 12;
    } else if (hour > 12){
      apm = 'PM';
      hour = hour - 12;
    } else if (hour === 12){
      apm = 'PM';
    }
    if (!options.includesAPM)
      apm = '';
    if (minutes !== 0)
      return hour + ":" + (minutes < 10 ? '0' : '') + minutes + apm;
    return hour + apm;
  },
  humanize_hour: function(hour){
    var apm = 'am';
    if (hour == 0) hour = 12;
    else if (hour >= 12) apm = 'pm';
    if (hour > 12) hour = hour - 12;
    return hour + " " + apm;
  },
  get_period_offset: function(period, height){
    var start = FunctionsContext.time_parts(period.get('start')),
        time = start.minute * 60 + start.second;
    return time / 3600.0 * height;
  },
  get_period_height: function(period, height){
    var t2s = FunctionsContext.time_to_seconds;
    var time = t2s(period.get('end')) - t2s(period.get('start'));
    //return 25 // 30 min time block
    //return 41.666666667 // 50 min time block
    return time / 3600.0 * height;
  }
};

