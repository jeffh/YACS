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
		//return new BackgroundWorker(
			_.map(conflicts, rawObject),
			_.map(sections, rawObject)
		);
	});

	// fast to check, but misses cyclic conflicts
	this.conflictsWith = function(courseIdsToSectionIds, sectionIdString){
		return this.promise.then(function(validator){
			var result = validator.conflictsWith(courseIdsToSectionIds, sectionIdString);
			var err = result[0],
				conflict = result[1];
			return conflict;
		});
	};

	// slower, but checks for cyclic conflicts
	this.isValid = function(courseIdsToSectionIds){
		return this.promise.then(function(validator){
			return validator.isValid(courseIdsToSectionIds);
		});
	};

	this.computeSchedules = function(courseIdsToSectionIds, num){
		return this.promise.then(function(validator){
			return _.map(validator.computeSchedules(courseIdsToSectionIds, num), function(schedule){
				var mappedSchedule = {};
				_.each(schedule, function(section, courseId){
					mappedSchedule[courseId] = idToSection[section.id];
				});
				return mappedSchedule;
			});
		});
	};
});

})(angular, app);

