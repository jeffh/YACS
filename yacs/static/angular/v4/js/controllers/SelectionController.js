'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', function($window, $scope, $q, Selection, currentSemesterPromise, CourseFetcher, schedulePresenter){
	$scope.courses = [];
	$scope.hideSearchBar = true;
	$scope.emptyText = "You didn't select any courses. They would go here.";

	$q.all([currentSemesterPromise, Selection.current]).then(function(values){
		var semester = values[0];
		var selection = values[1];
		var filters = {
			semester_id: semester.id,
			id: selection.courseIds()
		};

		function refreshAndSave(shouldSave){
			if (shouldSave){
				selection.save();
			}
			selection.apply($scope.courses);
			$scope.schedules = schedulePresenter(selection.schedules());
			$scope.scheduleIndex = 0;
		}

		if (selection.numberOfCourses()){
			CourseFetcher(filters).then(function(courses){
				$scope.courses = courses;
				refreshAndSave(false);
			});
		}

		$scope.showClearButton = function(){
			return selection.numberOfCourses();
		};

		$scope.clickCourse = function(course){
			selection.updateCourse(course).then(function(){
				refreshAndSave(true);
			}, function(err){
				refreshAndSave(false);
			});
		};

		$scope.clickSection = function(course, section){
			selection.updateSection(course, section).then(function(){
				refreshAndSave(true);
			}, function(err){
				refreshAndSave(false);
			});
		};

		$scope.clickClearSelection = function(){
			selection.clear();
			refreshAndSave(true);
		};

		$scope.keyDown = function(event){
			var left = 37, right = 39;
			$scope.schedules.then(function(schedules){
				if (event.keyCode === left){
					$scope.scheduleIndex = Math.max($scope.scheduleIndex - 1, 0);
				} else if (event.keyCode === right){
					$scope.scheduleIndex = Math.min($scope.scheduleIndex + 1, schedules.length - 1);
				}
			});
		};
	});
});

})(angular, app);

