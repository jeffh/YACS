'use strict';

(function(angular, app, undefined){

app.controller('SearchResultsCtrl', function($scope, $routeParams, $location, CourseFetcher, CourseSearch, urlProvider){
	$scope.courses = [];
	var query = decodeURIComponent($routeParams.query || '');
	$scope.semester.then(function(semester){
		if (query == '') {
			return;
		}
		CourseFetcher({semester_id: semester.id}).then(function(allCourses){
			$scope.courses = CourseSearch(allCourses, $routeParams.query);
		});
	});
});

})(angular, app);

