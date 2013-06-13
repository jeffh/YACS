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
			selection.apply(courses);
		});
	});

	function apply(selection){
		return function(){
			selection.apply($scope.courses);
		};
	}
	function saveAndApply(selection){
		return function(){
			selection.save();
			apply(selection)();
		};
	}

	$scope.clickCourse = function(course){
		selectionPromise.then(function(selection){
			selection.updateCourse(course).then(
				saveAndApply(selection),
				apply(selection));
		});
	};

	$scope.clickSection = function(course, section){
		selectionPromise.then(function(selection){
			selection.updateSection(course, section).then(
				saveAndApply(selection),
				apply(selection));
		});
	};
});

})(angular, app);

