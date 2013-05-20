'use strict';

(function(document, angular, app, undefined){

app.factory('Model', function(apiClient){
	var callOrReturn = function(fn, args){
		if (angular.isFunction(fn)){
			return fn.apply(window, args);
		}
		return fn;
	};
	return function(name, options){
		options = options || {};
		var Model = eval('(function ' + name + '(){ this.initialize.apply(this, arguments); })');
		Model.prototype = {};

		angular.extend(Model, {
			query: function(filters){
				filters = filters || {};
				var promise = apiClient.get(callOrReturn(options.query, [filters]), filters);
				return promise.then(function(result){
					var collection = [];
					for (var i=0; i<result.length; i++) {
						collection.push(new Model(result[i]));
					}
					return collection;
				});
			},
			get: function(id) {
				var promise = apiClient.get(callOrReturn(options.get, [id]));
				return promise.then(function(result){
					return new Model(result);
				});
			}
		});

		angular.extend(Model.prototype, {
			initialize: function(attributes){
				angular.extend(this, angular.copy(options.defaults || {}), attributes);
			},
			refresh: function(){
				var self = this;
				var promise = apiClient.get(callOrReturn(options.get, [id]));
				return promise.then(function(result){
					angular.extend(self, result);
					return self;
				});
			},
			equals: function(model){
				return this.id == model.id;
			}
		});

		return Model;
	};
});

var URL = function(base_url){
	return function(id){
		return angular.isNumber(id) ? base_url + id : base_url;
	};
};

app.factory('Semester', function(Model){
	var url = URL('/api/4/semesters/');
	/*
	 * name: "Spring 2013",
	 * year: 2013,
	 * date_updated: "2013-03-05T22:34:57.904120",
	 * ref: "http://sis.rpi.edu/reg/zs201301.htm",
	 * id: 2,
	 * month: 1
	 */
	var Semester = Model('Semester', {
		query: url,
		get: url
	});
	angular.extend(Semester, {
		latest: function(){
			return Semester.query().then(function(semesters){
				return semesters[0];
			});
		}
	});
	return Semester;
});

app.factory('Course', function(Model, Section){
	var url = URL('/api/4/courses/');
	/*
	 * description: "",
	 * is_comm_intense: false,
	 * min_credits: 0,
	 * grade_type: "Satisfactory/Unsatisfactory",
	 * number: 1010,
	 * max_credits: 0,
	 * prereqs: "",
	 * department_id: 38,
	 * id: 923,
	 * name: "ORAL COMM FOR TA'S"
	 *
	 * Added:
	 * sections: []
	 * department: {}
	 */
	var Course = Model('Course', {
		defaults: {sections: [], department: {}, tags: []},
		query: url,
		get: url
	});
	var pluralize = function(word, num){
		return (num === 1) ? word : word + 's';
	};
	angular.extend(Course.prototype, {
		seatsLeft: function(){
			// it's possible for seatsTaken() > seatsTotal(),
			// so we need to compute this manually
			return _(this.sections).reduce(function(i, section, num){
				return Math.max(section.seats_total - section.seats_taken, 0) + num;
			}, 0);
		},
		seatsTaken: function(){
			return _(this.sections).reduce(function(i, section, num){
				return section.seats_taken + num;
			}, 0);
		},
		seatsTotal: function(){
			return _(this.sections).reduce(function(i, section, num){
				return section.seats_total + num;
			}, 0);
		},
		sectionsText: function(){
			var n = this.sections.length;
			return n + pluralize(' section', n);
		},
		seatsLeftText: function(){
			var n = this.seatsLeft();
			return n + pluralize(' seat', n);
		},
		sectionTypes: function(){
			return _(this.sections).chain().pluck('section_times').flatten().pluck('kind').uniq().value();
		},
		creditsText: function(){
			if (this.min_credits === this.max_credits) {
				return this.min_credits + pluralize(' credit', this.min_credits);
			}
			return this.min_credits + ' - ' + this.max_credits + ' credits';
		},
		generateTags: function(){
			var tags = [];
			var kindAliases = {
				LEC: {
					name: 'Lecture',
					title: 'This course has lecture',
					sort_order: 0
				},
				REC: {
					name: 'Recitation',
					title: 'This course has recitation',
					sort_order: 2
				},
				LAB: {
					name: 'Lab',
					title: 'This course has lab',
					sort_order: 1
				},
				STU: {
					name: 'Studio',
					title: 'This course has studio',
					sort_order: 4
				}
			};
			_(this.sectionTypes()).each(function(type){
				tags.push(kindAliases[type] || {name: type});
			});
			if (this.is_comm_intense) {
				tags.push({
					name: 'Comm Intensive',
					title: 'This course count as a communication intensive course',
					classes: 'satisfies-requirement',
					sort_order: 10
				});
			}
			if (this.grade_type !== '') {
				tags.push({
					name: 'Pass/Fail',
					title: "This course's grading is pass or fail only.",
					classes: 'pass_or_fail',
					sort_order: 11
				});
			}
			// TODO: prereq & crosslist
			return _.sortBy(tags, 'sort_order');
		}
	});
	return Course;
});

app.factory('Department', function(Model){
	var url = URL('/api/4/departments/');
	/*
	 * code: "ADMN",
	 * id: 38,
	 * name: "Administration"
	 */
	var Department = Model('Department', {
		query: url,
		get: url
	});
	return Department;
});

app.factory('Section', function(Model){
	var url = URL('/api/4/sections/');
	/*
	 * course_id: 1,
	 * seats_total: 50,
	 * crosslisted_id: null,
	 * semester_id: 1,
	 * id: 1,
	 * notes: "",
	 * section_times: [
	 *	   {
	 *	   start: "10:00:00",
	 *	   kind: "LEC",
	 *	   end: "11:50:00",
	 *	   location: "",
	 *	   instructor: "Zhang",
	 *	   section_id: 1,
	 *	   days_of_the_week: [
	 *		  "Monday",
	 *		  "Thursday"
	 *	   ]
	 *	   }
	 * ],
	 * crn: 95148,
	 * number: "01",
	 * seats_taken: 40
	 */
	var Section = Model('Section', {
		query: url,
		get: url
	});
	return Section;
});

})(document, angular, app);

