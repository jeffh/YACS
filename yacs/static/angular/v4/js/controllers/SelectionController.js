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
	});
});

})(angular, app);

