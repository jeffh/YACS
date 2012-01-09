//////////////////////////////// Class object ////////////////////////////////
// Based on john resig's simple javascript inheritance
(function(window, $, undefined){
var initializing = false;

window.Class = function (){};
window.Class.extend = function(attributes){
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
window.Utils = {
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
  }
}

})(window, jQuery);

//////////////////////////////// Core functions ////////////////////////////////
function assert(bool, message){
  if (bool){
    if (message)
      throw message;
    else
      throw "Assertion failed";
  }
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
		return this.indexOf(str) === this.length - str.length;
	},
	trim: function(){
		return $.trim(this);
	},
	toInteger: function(base){
		return parseInt(this, base || 10);
	},
	toFloat: function(){
		return parseFloat(this);
	}
});

$.extend(Number.prototype, {
	toInteger: String.prototype.toInteger,
	toFloat: String.prototype.toFloat
});

$.extend(Array.prototype, {
	contains: function(value){
		for(var i=0, l=this.length; i<l; i++)
			if (this[i] === value)
              return true;
        return false;
    },
	map: function(fn){
		var accum = [];
		for(var i=0, l=this.length; i<l; i++)
			accum.push(fn.call(this[i], this[i], i));
		return accum;
	},
	filter: function(fn){
		var accum = [];
		for(var i=0, l=this.length; i<l; i++){
			if(fn.call(this[i], this[i], i))
				accum.push(this[i]);
		}
		return accum;
	},
    pushUnique: function(value){
      if (!this.contains(value))
        return this.push(value) || true;
      return false;
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

$.extend(Function.prototype, {
	bind: function(obj){
		return (function(self){
			return function(){ self.apply(obj, arguments); };
		})(this);
	}
});

//////////////////////////////// Helper Objects ////////////////////////////////
var Fuse = Class.extend({
	timer: null,
	options: {
		delay: 200,
		trigger: function(){},
		cancelled: function(){}
	},
	init: function(options){
		this.options = $.extend({}, this.options, options);
	},
	start: function(delay){
		this.stop();
		var self = this;
		this.timer = setTimeout(function(){
			self.trigger();
		}, delay !== undefined ? delay : this.options.delay);
	},
	stop: function(suppressCancelEvent){
		if (this.timer){
			clearTimeout(this.timer);
			this.timer = null;
			if (!suppressCancelEvent)
				this.options.cancelled.call(this);
		}
	},
	trigger: function(){
		this.options.trigger.call(this);
		this.timer = null;
	}
});

//////////////////////////////// Realtime Search ////////////////////////////////

var RealtimeForm = Class.extend({
	options: {
		updateElement: $(),
		success: function(value){ this.html(value); },
		error: function(){ console.error('failed realtime form:', arguments); },
		complete: $.noop,
		activityIndicatorElement: '#search-spinner',
		showActivityIndicator: function(){
			$(this.options.activityIndicatorElement).show();
		},
		hideActivityIndicator: function(){
			$(this.options.activityIndicatorElement).hide();
		},
		dataType: undefined,
		url: null,
		method: null,
		cache: false,
		additionalPOST: '',
		additionalGET: '',
		suppressFormSubmit: false,
		triggerDelay: 200,
		customHandler: null
	},
	init: function(form, options){
		this.options = $.extend({}, this.options, options);
		this.form = $(form);
		this.fuse = new Fuse({
			delay: this.options.triggerDelay,
			trigger: this.sendRequest.bind(this),
			cancelled: this.stopRequest.bind(this)
		});
		this.attachEvents();
	},
	getOption: function(name, defaultFn){
		if (this.options[name])
			return this.options[name];
		return defaultFn.apply(this);
	},
	getURL: function(){
		return this.getOption('url', function(){
			return this.form.attr('action');
		});
	},
	getMethod: function(){
		return this.getOption('method', function(){
			return this.form.attr('method');
		});
	},
	getMethodData: function(){
		var formMethod = this.form.attr('method').toUpperCase(),
			type = this.getMethod().toUpperCase();
		if(type === 'GET'){
			var data = formMethod === 'GET' ? this.form.serialize() : {},
				params = this.options.additionalGET;
			return data + '&' + (typeof params === 'object' ? $.param(params) : params);
		} else if(type === 'POST'){
			var data = formMethod === 'POST' ? this.form.serialize() : {},
				params = this.options.additionalPOST;
			return data + '&' + (typeof params === 'object' ? $.param(params) : params);
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
		console.log('send', this.getURL(), this.getMethodData());
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
			if (this.options.customHandler(this.form, this.fuse))
				this.hideActivityIndicator();
		} else {
			this.fuse.start();
		}
	},
	formSubmitted: function(evt){
		if (this.options.suppressFormSubmit){
			this.initiateRequest();
		}
		return !this.options.suppressFormSubmit;
	},
	changed: function(evt){
		console.log(evt.type, evt);
		this.initiateRequest();
	},
	showActivityIndicator: function(){
		this.options.showActivityIndicator.call(this);
	},
	hideActivityIndicator: function(){
		this.options.hideActivityIndicator.call(this);
	},
	keyDownSelector: 'input[type=text], input[type=search], textarea',
	detachEvents: function(){
		if (this.options.suppressFormSubmit && this._formSubmitted)
			this.form.unbind('submit', this._formSubmit);

		if (this._changed){
			var self = this;
			this.form.find('input, textarea, select').each(function(){
				var $el = $(this);
				if ($el.is(self.keyDownSelector))
					$el.unbind('keyup', self._changed);
				if (this._formSubmitted && $el.is('input[type=search]'))
					$el.unbind('search', self._formSubmitted);
				$el.unbind('change', self._changed);
			});
		}
		if (this._formSubmitted){
			this.form.submit(this._formSubmit);
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
			$el.bind('change', self._changed);
		});

		if (this.options.suppressFormSubmit){
			this._formSubmitted = this.formSubmitted.bind(this);
			this.form.submit(this._formSubmit);
		}
	}
});

//////////////////////////////// Course Selection ////////////////////////////////
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
      id: Utils.integer($el.attr('data-cid')),
      CRNs: $el.attr('data-crns').split(',').filter(String.prototype.isBlank).map(Utils.integer),
      fullCRNs: $el.attr('data-crns-full').split(',').filter(String.prototype.isBlank).map(Utils.integer)
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
  update: function(){
    // write crns to server
  },
  set: function(selected){
    // read crns from the DOM
    this.course_ids = [];
    this.crns = selected;
    for (var cid in this.crns){
      if(this.crns.hasOwnProperty(cid))
        this.course_ids.push(cid.toInteger());
    }
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

