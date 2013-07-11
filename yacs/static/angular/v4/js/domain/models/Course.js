'use strict';

(function(angular, app, undefined){

app.factory('Course', ['ModelFactory', 'Section', 'tagger', 'Utils', 'conflictor',
			function(ModelFactory, Section, tagger, Utils, conflictor){
	var url = Utils.URL('/api/4/courses/');
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
	 * tags: []
	 * is_selected: false
	 * notes: []
	 * conflicts: []
	 */
	var Course = ModelFactory('Course', {
		defaults: {
			sections: [],
			department: {},
			tags: [],
			is_selected: false,
			conflicts: []
		},
		query: url,
		get: url
	});
	angular.extend(Course.prototype, {
		instructors: function(){
			return _(this.sections).chain().map(function(section){
				return _.pluck(section.section_times, 'instructor');
			}).uniq().value();
		},
		seatsLeft: function(){
			// it's possible for seatsTaken() > seatsTotal(),
			// so we need to compute this manually
			return _(this.sections).reduce(function(num, section){
				return Math.max(section.seats_total - section.seats_taken, 0) + num;
			}, 0);
		},
		seatsTaken: function(){
			return _(this.sections).reduce(function(num, section){
				return section.seats_taken + num;
			}, 0);
		},
		seatsTotal: function(){
			return _(this.sections).reduce(function(num, section){
				return section.seats_total + num;
			}, 0);
		},
		sectionsText: function(){
			var n = this.sections.length;
			return n + Utils.pluralize(' section', n);
		},
		seatsLeftText: function(){
			var n = Math.max(this.seatsLeft(), 0);
			return n + Utils.pluralize(' seat', n);
		},
		sectionTypes: function(){
			return _(this.sections).chain().pluck('section_times').flatten().pluck('kind').uniq().value();
		},
		creditsText: function(){
			if (this.min_credits === this.max_credits) {
				return this.min_credits + Utils.pluralize(' credit', this.min_credits);
			}
			return this.min_credits + ' - ' + this.max_credits + ' credits';
		},
		computeProperties: function(){
			conflictor.computeCourseConflicts(this);
			this.tags = tagger(this);
			this.notes = _(this.sections).chain().pluck('notes').uniq().value();
		}
	});
	return Course;
}]);

app.factory('currentCourses', ['currentSemesterPromise', 'Course', '$q',
			function(currentSemesterPromise, Course, $q){
	var deferred = $q.defer();
	currentSemesterPromise.then(function(semester){
		Course.query({semester_id: semester.id}).then(function(courses){
			deferred.resolve(courses);
		});
	});
	return deferred.promise;
}]);

})(angular, app);

