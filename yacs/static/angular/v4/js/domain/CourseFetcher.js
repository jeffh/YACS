'use strict';

(function(angular, app, undefined){

app.factory('CourseFetcher', ['$q', '$timeout', 'Course', 'Department',
			'Section', 'Utils', 'networkIndicator',
			function($q, $timeout, Course, Department,
					 Section, Utils, networkIndicator){
	return function(filters){
		networkIndicator.acquire();
		var deferred = $q.defer();
		var deptPromise = Department.query({semester_id: filters.semester_id});
		var coursePromise = Course.query(filters);
		$q.all([deptPromise, coursePromise]).then(function(values){
			var departments = values[0];
			var courses = values[1];
			var idToDept = Utils.hashById(departments);
			var idToCourse = Utils.hashById(courses);
			_(courses).each(function(course){
				course.department = idToDept[course.department_id];
				course.sections = [];
			});

			var sectionPromise = Section.query({
				semester_id: filters.semester_id,
				course_id: _(idToCourse).chain().keys().uniq().sort().value()
			});
			$timeout(function(){
				sectionPromise.then(function(sections){
					_(sections).each(function(section){
						idToCourse[section.course_id].sections.push(section);
					});
					_(courses).each(function(course){
						course.computeProperties();
						course.sections = _.sortBy(course.sections, 'number');
					});
					deferred.resolve(courses);
				}, function(error){
					deferred.reject(error);
				});
			}, 100);
		}, function(error){
			deferred.reject(error);
		});

		function releaseIndicator(result){
			networkIndicator.release();
			return result;
		}

		return deferred.promise.then(releaseIndicator, releaseIndicator);
	};
}]);

})(angular, app);

