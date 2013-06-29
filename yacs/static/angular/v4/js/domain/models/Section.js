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
			conflicts: [],
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
			this.__cache__ = {};
		},
		seatsLeft: function(){
			return this.seats_total - this.seats_taken;
		},
		seatsLeftText: function(){
			if (!this.__cache__.seatsLeftText){
				var n = Math.max(this.seatsLeft(), 0);
				this.__cache__.seatsLeftText = n + Utils.pluralize(' seat', n);
			}
			return this.__cache__.seatsLeftText;
		},
		instructorsText: function(){
			if (!this.__cache__.instructorsText){
				var instructors = _(this.section_times).chain().pluck('instructor').uniq().value();
				this.__cache__.instructorsText = instructors.join(', ');
			}
			return this.__cache__.instructorsText;
		},
		numberText: function(){
			var str = parseInt(this.number, 10);
			return (isNaN(str) ? this.number : str);
		},
		hasMultipleTimesPerDay: function(){
			if (typeof(this.__cache__.hasMultipleTimesPerDay) === 'undefined'){
				this.__cache__.hasMultipleTimesPerDay = _.some(this.times, function(time){
					return time.count > 1;
				});
			}
			return this.__cache__.hasMultipleTimesPerDay;
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
				var numberOfTimes = dowToSectionTime[dow].length;
				times.push({
					day_of_the_week: dow.substr(0, 3),
					count: numberOfTimes,
					classes: numberOfTimes ? 'has_times' : 'has_no_times',
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

