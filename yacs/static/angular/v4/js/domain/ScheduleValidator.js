'use strict';

(function(angular, app, undefined){

app.service('scheduleValidator', function($q, Conflict, Semester, Section, Time, Utils, currentSemesterPromise, BackgroundWorker){
	var conflictsDeferred = $q.defer();
	var sectionsDeferred = $q.defer();
	var idToSection = {};
	currentSemesterPromise.then(function(semester){
		Conflict.query({semester_id: semester.id}).then(function(conflicts){
			conflictsDeferred.resolve(conflicts);
		}, _.bind(conflictsDeferred.reject, conflictsDeferred));
		Section.query({semester_id: semester.id}).then(function(sections){
			idToSection = Utils.hashById(sections);
			sectionsDeferred.resolve(sections);
		}, _.bind(sectionsDeferred.reject, sectionsDeferred));
	});
	this.promise = $q.all([conflictsDeferred.promise, sectionsDeferred.promise]).then(function(values){
		var conflicts = values[0];
		var sections = values[1];

		function rawObject(obj){ return obj.toObject(); }

		return new AppWorker.ScheduleValidator(
			_.map(conflicts, rawObject),
			_.map(sections, rawObject)
		);
	});

	// fast to check, but misses cyclic conflicts
	this.conflictsWith = function(courseIdsToSectionIds, sectionIdString){
		var deferred = $q.defer();
		this.promise.then(function(validator){
			validator.conflictsWith(courseIdsToSectionIds, sectionIdString, function(result){
				var err = result[0],
					conflict = result[1];
				deferred.resolve(conflict);
			});
		});
		return deferred.promise;
	};

	// slower, but checks for cyclic conflicts
	this.isValid = function(courseIdsToSectionIds){
		var deferred = $q.defer();
		this.promise.then(function(validator){
			validator.isValid(courseIdsToSectionIds, function(isValid){
				deferred.resolve(isValid);
			});
		});
		return deferred.promise;
	};

	this.computeSchedules = function(courseIdsToSectionIds, num){
		var deferred = $q.defer();
		this.promise.then(function(validator){
			validator.computeSchedules(courseIdsToSectionIds, num, function(schedules){
				var mappedSchedules = _.map(schedules, function(schedule){
					var mappedSchedule = {};
					_.each(schedule, function(section, courseId){
						mappedSchedule[courseId] = idToSection[section.id];
					});
					return mappedSchedule;
				});
				deferred.resolve(mappedSchedules);
			});
		});
		return deferred.promise;
	};
});

})(angular, app);

