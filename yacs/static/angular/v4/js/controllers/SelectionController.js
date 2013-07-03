'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', function($window, $scope, $q, Selection, currentSemesterPromise, CourseFetcher, schedulePresenter, SectionTime){
	$scope.courses = [];
	$scope.hideSearchBar = true;
	$scope.emptyText = "You didn't select any courses. They would go here.";
	$scope.scheduleIndex = 0;

	$q.all([currentSemesterPromise, Selection.current]).then(function(values){
		var semester = values[0];
		var selection = values[1];
		var filters = {
			semester_id: semester.id,
			id: selection.courseIds()
		};
		var blockedTimes = [];

		function refreshAndSave(shouldSave){
			if (shouldSave){
				selection.save();
			}
			selection.apply($scope.courses);
			$scope.schedules = schedulePresenter(
				selection.schedules(_.map(blockedTimes, function(sectionTime){
					return sectionTime.toObject();
				})),
				blockedTimes
			).then(function(schedules){
				$scope.scheduleIndex = Math.min($scope.scheduleIndex, schedules.length - 1);
				return schedules;
			});
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

		$scope.toggleBlockableTime = function(time, dow){
			blockedTimes.push(new SectionTime({
				days_of_the_week: [dow],
				start: time.toObject(),
				end: _.extend({}, time, {minute: 59}).toObject()
			}));
			refreshAndSave(false);
		};

		$scope.isBlocked = function(time, dow){
			return _.any(blockedTimes, function(blockedTime){
				return blockedTime.start === time.toObject() && dow === blockedTime.days_of_the_week[0];
			});
		};
	});
});

})(angular, app);

