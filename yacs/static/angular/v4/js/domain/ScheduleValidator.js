'use strict';

(function(angular, app, undefined){

app.service('scheduleValidator', function($q, Conflict, Semester, Section, Time, Utils, currentSemesterPromise){
	var conflictsDeferred = $q.defer();
	var sectionsDeferred = $q.defer();
	currentSemesterPromise.then(function(semester){
		Conflict.query({semester_id: semester.id}).then(function(conflicts){
			var conflictMap = Utils.hashById(conflicts);
			conflictsDeferred.resolve(conflictMap);
		}, _.bind(conflictsDeferred.reject, conflictsDeferred));
		Section.query({semester_id: semester.id}).then(function(sections){
			var idToSection = Utils.hashById(sections);
			sectionsDeferred.resolve(idToSection);
		}, _.bind(sectionsDeferred.reject, sectionsDeferred));
	});
	this.promise = $q.all([conflictsDeferred.promise, sectionsDeferred.promise]);

	// fast to check, but misses cyclic conflicts
	this.conflictsWith = function(courseIdsToSectionIds, sectionIdString){
		return this.promise.then(function(values){
			var sectionId = parseInt(sectionIdString, 10);
			var conflictMap = values[0];
			var idToSection = values[1];
			var lastConflict = null;
			var conflictsForSectionId = conflictMap[sectionId];
			if (_.isEmpty(conflictsForSectionId)){
				console.warn('missing precomputed conflicts for', sectionIdString, '->', sectionId);
				return false;
			}
			_(_.keys(courseIdsToSectionIds)).some(function(courseId){
				var selectedSectionIds = courseIdsToSectionIds[courseId];
				return _(selectedSectionIds).some(function(sid){
					if (conflictsForSectionId.conflictsWith(sid)){
						lastConflict = {
							selectionSection: idToSection[sid],
							section: idToSection[sectionId]
						};
					}
					return lastConflict;
				});
			});
			return lastConflict;
		});
	};

	// slower, but checks for cyclic conflicts
	this.isValid = function(courseIdsToSectionIds){
		return this.computeSchedules(courseIdsToSectionIds, 1).then(function(schedules){
			return schedules.length;
		});
	};
	this.computeSchedules = function(courseIdsToSectionIds, num){
		var self = this;
		var deferred = $q.defer();
		var courseIds = _(courseIdsToSectionIds).keys();
		var sectionIds = _(courseIdsToSectionIds).chain().values().flatten().uniq().value();
		this.promise.then(function(values){
			var conflicts = values[0];
			var idToSections = values[1];
			var sectionDomains = _(courseIdsToSectionIds).chain(
			).values().map(function(sectionIds){
				return _.map(sectionIds, function(id){
					return idToSections[id];
				});
			}).value();

			var possibleSchedules = Utils.product(sectionDomains);
			var validSchedules = [];
			_(possibleSchedules).all(function(schedule){
				if (self._isValidSchedule(schedule)){
					validSchedules.push(_.object(courseIds, schedule));
				}
				return !num || validSchedules.length < num;
			});
			deferred.resolve(validSchedules);
		}, function(err){
			deferred.reject(err);
		});
		return deferred.promise;
	};

	this._isValidSchedule = function(schedule){ // schedule = array of sections
		var self = this;
		return _(schedule).all(function(section1, i){
			return _(schedule).all(function(section2, j){
				if (i >= j) {
					return true; // continue
				}

				return !self._areSectionsConflicted(section1, section2);
			});
		});
	};

	this._areSectionsConflicted = function(section1, section2){
		var self = this;
		return _(section1.section_times).some(function(time1){
			return _(section2.section_times).some(function(time2){
				return self._areTimesConflicted(time1, time2);
			});
		});
	};

	this._areTimesConflicted = function(time1, time2){
		var dows = _(time1.days_of_the_week).intersection(time2.days_of_the_week);
		var startTime1 = new Time(time1.start).totalSeconds;
		var startTime2 = new Time(time2.start).totalSeconds;
		var endTime1 = new Time(time1.end).totalSeconds;
		var endTime2 = new Time(time2.end).totalSeconds;
		return dows.length && (
			(startTime1 <= startTime2 && startTime2 <= endTime1) ||
			(startTime2 <= startTime1 && startTime1 <= endTime2) ||
			(startTime1 <= endTime2 && endTime2 <= endTime1) ||
			(startTime2 <= endTime1 && endTime1 <= endTime2)
		);
	};
});

})(angular, app);

