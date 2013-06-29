'use strict';
// requires underscore
// requires AppWorker.Namespace
// requires AppWorker.Utils

AppWorker.ScheduleValidator = function(conflictsObjects, sectionObjects){
	var conflictMap = AppWorker.Utils.hashById(conflictsObjects);
	var idToSection = AppWorker.Utils.hashById(sectionObjects);
	var self = this;

	var memoize = function(fn, keyfn){
		var cache = {};
		keyfn = JSON.stringify;
		return function(){
			var key = keyfn([this, _.toArray(arguments)]);
			if (typeof cache[key] === 'undefined') {
				cache[key] = fn.apply(this, arguments);
			}
			return cache[key];
		};
	};

	// computes a quick conflict check. Faster to check if there are any
	// conflicts, but is not accurate. If conflicts exist, the slower
	// check must be used.
	// 
	// This can also be used to guess what course conflicts with what.
	// 
	// returns err, conflict={selectionSectionObj, sectionObj}
	// where either the error or conflict is returned as not-null
	this.conflictsWith = function(courseIdsToSectionIds, sectionIdString, callback){
		var sectionId = parseInt(sectionIdString, 10);
		var lastConflict = null;
		var conflictsForSectionId = conflictMap[sectionId];
		if (_.isEmpty(conflictsForSectionId)){
			var msg = 'missing precomputed conflicts for ' + sectionIdString + ' -> ' + sectionId;
			callback([msg, null]);
			return;
		}
		_(_.keys(courseIdsToSectionIds)).some(function(courseId){
			var selectedSectionIds = courseIdsToSectionIds[courseId];
			return _(selectedSectionIds).some(function(sid){
				if (_.contains(conflictsForSectionId.conflicts, sid)){
					lastConflict = {
						selectionSection: idToSection[sid],
						section: idToSection[sectionId]
					};
				}
				return lastConflict;
			});
		});
		callback([null, lastConflict]);
	};

	// slower, but accurate (checks for cyclic conflicts). It is unable
	// to identify which courses conflict with each other.
	// 
	// returns true/false if the given selection of {courseIds: [sectionIds]}
	// is a valid schedule
	this.isValid = function(courseIdsToSectionIds, callback){
		this.computeSchedules(courseIdsToSectionIds, 1, function(schedules){
			callback(schedules.length);
		});
	};

	this.computeSchedules = function(courseIdsToSectionIds, num, callback){
		var self = this;
		var courseIds = _.keys(courseIdsToSectionIds);
		var sectionIds = _(courseIdsToSectionIds).chain().values().flatten().uniq().value();
		var sectionDomains = _(courseIdsToSectionIds).chain().values().map(function(sectionIds){
			return _.map(sectionIds, function(id){
				return idToSection[id];
			});
		}).value();

		var possibleSchedules = AppWorker.Utils.product(sectionDomains);
		var validSchedules = [];
		for (var i=0; i<possibleSchedules.length; i++){
			var schedule = possibleSchedules[i];
			if (self._isValidSchedule(schedule)){
				validSchedules.push(_.object(courseIds, schedule));
			}
			if (num && validSchedules.length >= num){
				break;
			}
		}
		callback(validSchedules);
	};

	this._isValidSchedule = function(schedule){ // schedule = array of sections
		for(var i=0; i<schedule.length - 1; i++){
			var section1 = schedule[i];
			for(var j=i + 1; j<schedule.length; j++){
				var section2 = schedule[j];
				if (this._areSectionsConflicted(section1, section2)){
					return false;
				}
			}
		}
		return true;
	};

	this._areSectionsConflicted = function(section1, section2){
		for(var i=0; i<section1.section_times.length; i++){
			var time1 = section1.section_times[i];
			for(var j=0; j<section2.section_times.length; j++){
				var time2 = section2.section_times[j];
				if (this._areTimesConflicted(time1, time2)){
					return true;
				}
			}
		}
		return false;
	};

	this._areTimesConflicted = function(time1, time2){
		var dows = _.intersection(time1.days_of_the_week, time2.days_of_the_week);
		if (!dows.length) {
			return false;
		}
		var startTime1 = this._totalSecondsForTime(time1.start);
		var startTime2 = this._totalSecondsForTime(time2.start);
		var endTime1 = this._totalSecondsForTime(time1.end);
		var endTime2 = this._totalSecondsForTime(time2.end);
		return (
			(startTime1 <= startTime2 && startTime2 <= endTime1) ||
			(startTime2 <= startTime1 && startTime1 <= endTime2) ||
			(startTime1 <= endTime2 && endTime2 <= endTime1) ||
			(startTime2 <= endTime1 && endTime1 <= endTime2)
		);
	};

	this._totalSecondsForTime = memoize(function(str){
		var parts = _(str.split(':')).map(function(i){ return parseInt(i, 10); });
		var hour = parts[0];
		var minute = parts[1];
		var second = parts[2];
		return parts[0] * 3600 + parts[1] * 60 + parts[2];
	});
};
