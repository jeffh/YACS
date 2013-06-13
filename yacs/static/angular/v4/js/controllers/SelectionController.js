'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', function($scope, $q, Selection, currentSemesterPromise, CourseFetcher){
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
		if (selection.numberOfCourses()){
			CourseFetcher(filters).then(function(courses){
				$scope.courses = courses;
				selection.apply(courses);
			});
		}

		$scope.showClearButton = function(){
			return selection.numberOfCourses();
		};

		$scope.clickCourse = function(course){
			selection.updateCourse(course).then(function(){
				selection.save();
				selection.apply($scope.courses);
			}, function(err){
				selection.apply($scope.courses);
			});
		};

		$scope.clickSection = function(course, section){
			selection.updateSection(course, section).then(function(){
				selection.save();
				selection.apply($scope.courses);
			}, function(err){
				selection.apply($scope.courses);
			});
		};

		$scope.clickClearSelection = function(){
			selection.clear();
			selection.save();
			selection.apply($scope.courses);
		};
	});
});

})(angular, app);

