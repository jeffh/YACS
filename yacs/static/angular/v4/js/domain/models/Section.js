'use strict';

(function(angular, app, undefined){

app.factory('Section', function(ModelFactory, SectionTime, Utils){
	var url = Utils.URL('/api/4/sections/');
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
	 *
	 * added:
	 * is_selected: false
	 * conflicts: [] // conflicts only for this section and not the course (computed by course)
	 * allConflicts: [] // all conflicts
	 */
	var Section = ModelFactory('Section', {
		defaults: {
			is_selected: false,
			allConflicts: [],
			conflicts: []
		},
		query: url,
		get: url
	});
	var superInit = Section.prototype.initialize;
	angular.extend(Section.prototype, {
		initialize: function(){
			superInit.apply(this, arguments);
			this.section_times = _(this.section_times).map(function(time){
				return new SectionTime(time);
			});
		},
		seatsLeft: function(){
			return this.seats_total - this.seats_taken;
		},
		seatsLeftText: function(){
			var n = Math.max(this.seatsLeft(), 0);
			return n + Utils.pluralize(' seat', n);
		},
		instructorsText: function(){
			var instructors = _(this.section_times).chain().pluck('instructor').uniq().value();
			return instructors.join(', ');
		},
		numberText: function(){
			var str = parseInt(this.number, 10);
			return (isNaN(str) ? this.number : str);
		},
		hasMultipleTimesPerDay: function(){
			return _.some(this.times, function(time){
				return time.count > 1;
			});
		},
		computeProperties: function(){
			this.times = this._generateDayTimes();
		},
		_generateDayTimes: function(){
			var times = [];
			var days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
			var dowToSectionTime = {};
			_(days_of_the_week).each(function(dow){
				dowToSectionTime[dow] = [];
			});
			_(this.section_times).each(function(section_time){
				_(section_time.days_of_the_week).each(function(dow){
					dowToSectionTime[dow].push(section_time);
				});
			});
			_(days_of_the_week).each(function(dow){
				times.push({
					day_of_the_week: dow.substr(0, 3),
					count: dowToSectionTime[dow].length,
					section_times: _.sortBy(dowToSectionTime[dow], function(section_time){
						return section_time.startTimeInSeconds();
					})
				});
			});
			return times;
		}
	});
	return Section;
});

})(angular, app);

