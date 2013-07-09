'use strict';

(function(angular, app, undefined){

app.controller('SelectionCtrl', function($window, $scope, $q, Selection, currentSemesterPromise, CourseFetcher, schedulePresenter, SectionTime, searchOptions){
	$scope.courses = [];
	$scope.emptyText = "You didn't select any courses. They would go here.";
	$scope.scheduleIndex = 0;
	searchOptions.visible = false;

	$q.all([currentSemesterPromise, Selection.current]).then(function(values){
		var semester = values[0];
		var selection = values[1];
		var filters = {
			semester_id: semester.id,
			id: selection.courseIds()
		};
		var blockedTimes = {};

		function refreshAndSave(shouldSave){
			if (shouldSave){
				selection.save();
			}
			selection.apply($scope.courses);
			var schedulesPromise = selection.schedules(_.map(blockedTimes, function(sectionTime){
				return sectionTime.toObject();
			}));

			$scope.schedules = schedulePresenter(schedulesPromise, _.values(blockedTimes));
			$scope.schedules.then(function(schedules){
				$scope.scheduleIndex = Math.min($scope.scheduleIndex, schedules.length - 1);
				$scope.schedule = schedules[$scope.scheduleIndex];
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

		$scope.previousSchedule = function(){
			$scope.schedules.then(function(schedules){
				$scope.scheduleIndex = Math.max($scope.scheduleIndex - 1, 0);
				$scope.schedule = schedules[$scope.scheduleIndex];
			});
		};

		$scope.nextSchedule = function(){
			$scope.schedules.then(function(schedules){
				$scope.scheduleIndex = Math.min($scope.scheduleIndex + 1, schedules.length - 1);
				$scope.schedule = schedules[$scope.scheduleIndex];
			});
		};

		$scope.keyDown = function(event){
			var left = 37, right = 39;
			if (event.keyCode === left){
				$scope.previousSchedule();
			} else if (event.keyCode === right){
				$scope.nextSchedule();
			}
		};

		$scope.isBlocked = function(time, dow){
			return blockedTimes[dow + '_' + time.toObject()];
		};

		$scope.toggleBlockableTime = function(time, dow){
			var key = dow + '_' + time.toObject();
			if ($scope.isBlocked(time, dow)){
				delete blockedTimes[key];
			} else {
				blockedTimes[key] = new SectionTime({
					days_of_the_week: [dow],
					start: time.toObject(),
					end: _.extend({}, time, {minute: time.minute + 29}).toObject()
				});
			}
			refreshAndSave(false);
		};
	});
});

})(angular, app);
