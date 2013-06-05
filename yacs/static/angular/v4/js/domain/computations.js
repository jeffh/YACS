'use strict';

(function(document, angular, app, undefined){

app.service('conflictor', function(){
	this.courseConflictNames = function(course){
		return _(course.sections).pluck('allConflicts');
	};

	this.isCourseConflicted = function(course){
		var conflictNamesList = this.courseConflictNames(course);
		return conflictNamesList.length && _(conflictNamesList).all(function(conflictNames){
			return conflictNames.length;
		});
	};

	this.courseConflictsAmongAllSections = function(course){
		var conflictNamesList = this.courseConflictNames(course);
		if (this.isCourseConflicted(course)){
			return _(conflictNamesList).chain().flatten().uniq().value();
		}
		return [];
	};

	this.computeCourseConflicts = function(course){
		course.conflicts = this.courseConflictsAmongAllSections(course);
		_(course.sections).each(function(section){
			section.computeProperties();
			var sectionNames = _.difference(section.allConflicts, course.conflicts);
			if (section.is_selected || _.isEqual(sectionNames, [])){
				section.conflicts = [];
			} else {
				section.conflicts = angular.copy(section.allConflicts);
			}
		});
	};
});

})(document, angular, app);

