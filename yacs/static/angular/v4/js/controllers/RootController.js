'use strict';

(function(angular, app, undefined){

app.controller('RootCtrl', ['$scope', '$location', '$window',
			   'currentSemesterPromise', 'Semester',
			   'Selection', 'STATIC_URL', 'networkIndicator',
			   function($scope, $location, $window,
						currentSemesterPromise, Semester,
						Selection, STATIC_URL, networkIndicator){
	$scope.STATIC_URL = STATIC_URL;
	$scope.networkIndicator = networkIndicator;

	Semester.query().then(function(semesters) {
		$scope.semesters = semesters;
	});

	$scope.changeToSemester = function(semester) {
		$location.path("/semesters/" + semester.year + "/" + semester.month + "/").search({});
		$scope.semester = semester;
	};

	currentSemesterPromise.then(function(semester){
		$scope.semester = semester;
	});

	Selection.current.then(function(selection){
		$scope.selection = selection;
	});
}]);

})(angular, app);

