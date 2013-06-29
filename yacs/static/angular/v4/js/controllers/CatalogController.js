'use strict';

(function(angular, app, undefined){

app.controller('CatalogCtrl', function($q, $scope, $location, $routeParams, $timeout, CourseFetcher, Selection, currentSemesterPromise){
	$scope.courses = [];
	$scope.emptyText = "Loading courses...";
	var selectionPromise = Selection.current;
	currentSemesterPromise.then(function(semester){
		var coursePromise = CourseFetcher({semester_id: semester.id, department_code: $routeParams.dept});
		$q.all([selectionPromise, coursePromise]).then(function(values){
			var selection = values[0];
			var courses = values[1];
			$scope.courses = courses;
			selection.apply($scope.courses);

			$scope.clickCourse = function(course){
				selection.updateCourse(course).then(function(){
					selection.save();
					selection.apply($scope.courses);
				}, function(){
					selection.apply($scope.courses);
				});
			};

			$scope.clickSection = function(course, section){
				selection.updateSection(course, section).then(function(){
					selection.save();
					selection.apply($scope.courses);
				}, function(){
					selection.apply($scope.courses);
				});
			};
		});
	});
});

})(angular, app);

