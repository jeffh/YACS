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

})(window, jQuery);

function not(fn){
  return function(){
    !fn.apply(this, arguments);
  }
}

//////////////////////////////// Extensions ////////////////////////////////
$.extend(jQuery.fn, {
  checked: function(){
    var checkboxes = this.filter('input[type=checkbox], input[type=radio]');
    if (arguments.length < 1)
      checkboxes.attr('checked');
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
      return this.trim() !== '';
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
			if(fn.call(this[i], this[i]))
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
          items = items.splice(i, 1);
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

//////////////////////////////// Model ////////////////////////////////
var Model = Class.extend({
	attributes: {},
	targets: {}, // attribute => selector
	init: function(attributes){
		this.attributes = $.extend({}, this.attributes, attributes);
	},
	keys: function(){
		var accum = [];
		for(var name in this.attributes)
			accum.push(name);
		return accum;
	},
	get: function(attr){ return this.attributes[name]; },
	has: function(attr){ return this.attributes[name] !== undefined; },
	update: function(attr, fn){
		this.set(fn(this.get(attr)));
	},
	set: function(attr, value, options){
		if (this.attributes[name] === value)
			return;
		var opt = $.extend({slient: false}, options),
			oldValue = value;
		this.attributes[name] = value;
		if (opt.slient)
			$(this).trigger('changed', [name, oldValue, value]);
	}
});
var Section = Model.extend({
	init: function(attributes){
		this._super(attributes);
	}
});

var Course = Model.extend({
	init: function(attributes){
		this.set('sections', []);
		this._super(attributes);
	},
	addSection: function(section){
		this.update('sections', function(arr){
			arr.push(section);
		});
	},
	getFreeSections: function(){
		this.get('sections').filter(function(section){
			return section.get('seats_total') - section.get('seats_left') > 0;
		});
	}
});

var Schedule = Model.extend({
	init: function(attributes){
		this.set('crns', []);
		this._super(attributes);
	}
});

var Selection = Class.extend({
	sections: [],
	init: function(){

	},
	addSection: function(section){
		if (section && section.get('crn'))
			this.crns.push(section.get('crn'));
	},
	addCourse: function(course){
		if (course && course.get('id'))
			this.cids.push(course.get('id'));
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

//////////////////////////////// UI Objects ////////////////////////////////

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
