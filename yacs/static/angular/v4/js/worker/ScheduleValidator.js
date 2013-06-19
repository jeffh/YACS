'use strict';

AppWorker.AsyncScheduleValidator = function(conflictsObjects, sectionObjects){
	var conflictMap = AppWorker.Utils.hashById(conflictsObjects);
	var idToSection = AppWorker.Utils.hashById(sectionObjects);
	var self = this;

    function asyncEach(items, options){
        items = _.toArray(items);
        var opt = _.extend({
            batchSize: 10,
            delay: 1,
            each: function(item, next){},
            complete: function(){}
        }, options);

        var index = -1;
        function next(){
            index++;
            if (index === items.length) {
                opt.complete();
                return;
            }
            var item = items[index];
            if (index % batchSize === 0) {
                setTimeout(function(){ nextitems[index](); }, opt.delay);
            } else {
                next();
            }
        }
        next.complete = opt.complete;
        next();
    }

	// computes a quick conflict check. Faster to check if there are any
	// conflicts, but is not accurate. If conflicts exist, the slower
	// check must be used.
	// 
	// This can also be used to guess what course conflicts with what.
	// 
	// returns err, conflict={selectionSectionObj, sectionObj}
	// where either the error or conflict is returned as not-null
	this.conflictsWith = function(courseIdsToSectionIds, sectionIdString){
		var sectionId = parseInt(sectionIdString, 10);
		var lastConflict = null;
		var conflictsForSectionId = conflictMap[sectionId];
		if (_.isEmpty(conflictsForSectionId)){
			var msg = 'missing precomputed conflicts for ' + sectionIdString + ' -> ' + sectionId;
			return [msg, null];
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
		return [null, lastConflict];
	};

	// slower, but accurate (checks for cyclic conflicts). It is unable
	// to identify which courses conflict with each other.
	// 
	// returns true/false if the given selection of {courseIds: [sectionIds]}
	// is a valid schedule
	this.isValid = function(courseIdsToSectionIds){
		return this.computeSchedules(courseIdsToSectionIds, 1).length;
	};

	this.computeSchedules = function(courseIdsToSectionIds, num){
		var self = this;
		var courseIds = _.keys(courseIdsToSectionIds);
		var sectionIds = _(courseIdsToSectionIds).chain().values().flatten().uniq().value();
		var sectionDomains = _(courseIdsToSectionIds).chain().values().map(function(sectionIds){
			return _.map(sectionIds, function(id){
				return idToSection[id];
			});
		}).value();

		var possibleSchedules = AppWorker.Utils.altProduct(sectionDomains);
		var validSchedules = [];
		_.all(possibleSchedules, function(schedule){
			if (self._isValidSchedule(schedule)){
				validSchedules.push(_.object(courseIds, schedule));
			}
			return !num || validSchedules.length < num;
		});
		return validSchedules;
	};

	this._isValidSchedule = function(schedule){ // schedule = array of sections
		var self = this;
		return _.all(schedule, function(section1, i){
			return _.all(schedule, function(section2, j){
				if (i >= j) {
					return true; // continue
				}

				return !self._areSectionsConflicted(section1, section2);
			});
		});
	};

	this._areSectionsConflicted = function(section1, section2){
		var self = this;
		return _.some(section1.section_times, function(time1){
			return _.some(section2.section_times, function(time2){
				return self._areTimesConflicted(time1, time2);
			});
		});
	};

	this._areTimesConflicted = function(time1, time2){
		var dows = _.intersection(time1.days_of_the_week, time2.days_of_the_week);
		var startTime1 = this._totalSecondsForTime(time1.start);
		var startTime2 = this._totalSecondsForTime(time2.start);
		var endTime1 = this._totalSecondsForTime(time1.end);
		var endTime2 = this._totalSecondsForTime(time2.end);
		return dows.length && (
			(startTime1 <= startTime2 && startTime2 <= endTime1) ||
			(startTime2 <= startTime1 && startTime1 <= endTime2) ||
			(startTime1 <= endTime2 && endTime2 <= endTime1) ||
			(startTime2 <= endTime1 && endTime1 <= endTime2)
		);
	};

	this._totalSecondsForTime = function(str){
		var parts = _(str.split(':')).map(function(i){ return parseInt(i, 10); });
		var hour = parts[0];
		var minute = parts[1];
		var second = parts[2];
		return parts[0] * 3600 + parts[1] * 60 + parts[2];
	};
};

// requires underscore
// requires AppWorker.Namespace
// requires AppWorker.Utils
AppWorker.ScheduleValidator = function(conflictsObjects, sectionObjects){
	var conflictMap = AppWorker.Utils.hashById(conflictsObjects);
	var idToSection = AppWorker.Utils.hashById(sectionObjects);
	var self = this;

	// computes a quick conflict check. Faster to check if there are any
	// conflicts, but is not accurate. If conflicts exist, the slower
	// check must be used.
	// 
	// This can also be used to guess what course conflicts with what.
	// 
	// returns err, conflict={selectionSectionObj, sectionObj}
	// where either the error or conflict is returned as not-null
	this.conflictsWith = function(courseIdsToSectionIds, sectionIdString){
		var sectionId = parseInt(sectionIdString, 10);
		var lastConflict = null;
		var conflictsForSectionId = conflictMap[sectionId];
		if (_.isEmpty(conflictsForSectionId)){
			var msg = 'missing precomputed conflicts for ' + sectionIdString + ' -> ' + sectionId;
			return [msg, null];
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
		return [null, lastConflict];
	};

	// slower, but accurate (checks for cyclic conflicts). It is unable
	// to identify which courses conflict with each other.
	// 
	// returns true/false if the given selection of {courseIds: [sectionIds]}
	// is a valid schedule
	this.isValid = function(courseIdsToSectionIds){
		return this.computeSchedules(courseIdsToSectionIds, 1).length;
	};

	this.computeSchedules = function(courseIdsToSectionIds, num){
		var self = this;
		var courseIds = _.keys(courseIdsToSectionIds);
		var sectionIds = _(courseIdsToSectionIds).chain().values().flatten().uniq().value();
		var sectionDomains = _(courseIdsToSectionIds).chain().values().map(function(sectionIds){
			return _.map(sectionIds, function(id){
				return idToSection[id];
			});
		}).value();

		var possibleSchedules = AppWorker.Utils.altProduct(sectionDomains);
		var validSchedules = [];
		_.all(possibleSchedules, function(schedule){
			if (self._isValidSchedule(schedule)){
				validSchedules.push(_.object(courseIds, schedule));
			}
			return !num || validSchedules.length < num;
		});
		return validSchedules;
	};

	this._isValidSchedule = _.memoize(function(schedule){ // schedule = array of sections
		var self = this;
		return _.all(schedule, function(section1, i){
			return _.all(schedule, function(section2, j){
				if (i >= j) {
					return true; // continue
				}

				return !self._areSectionsConflicted(section1, section2);
			});
		});
	});

	this._areSectionsConflicted = _.memoize(function(section1, section2){
		var self = this;
		return _.some(section1.section_times, function(time1){
			return _.some(section2.section_times, function(time2){
				return self._areTimesConflicted(time1, time2);
			});
		});
	});

	this._areTimesConflicted = _.memoize(function(time1, time2){
		var dows = _.intersection(time1.days_of_the_week, time2.days_of_the_week);
		var startTime1 = this._totalSecondsForTime(time1.start);
		var startTime2 = this._totalSecondsForTime(time2.start);
		var endTime1 = this._totalSecondsForTime(time1.end);
		var endTime2 = this._totalSecondsForTime(time2.end);
		return dows.length && (
			(startTime1 <= startTime2 && startTime2 <= endTime1) ||
			(startTime2 <= startTime1 && startTime1 <= endTime2) ||
			(startTime1 <= endTime2 && endTime2 <= endTime1) ||
			(startTime2 <= endTime1 && endTime1 <= endTime2)
		);
	});

	this._totalSecondsForTime = _.memoize(function(str){
		var parts = _(str.split(':')).map(function(i){ return parseInt(i, 10); });
		var hour = parts[0];
		var minute = parts[1];
		var second = parts[2];
		return parts[0] * 3600 + parts[1] * 60 + parts[2];
	});
};
