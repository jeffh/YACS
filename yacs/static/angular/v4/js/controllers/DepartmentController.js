'use strict';

(function(angular, app, undefined){

app.controller('DepartmentCtrl', ['$scope', '$location', 'Semester',
			   'Department', 'urlProvider', 'currentSemesterPromise',
			   function($scope, $location, Semester, Department, urlProvider, currentSemesterPromise){
	$scope.departments = [];

	currentSemesterPromise.then(function(semester){
		$scope.departments = Department.query({semester_id: semester.id});
		$scope.click = function(dept){
			$location.path(urlProvider(
				semester.year,
				semester.month,
				dept.code
			));
		};
	});
}]);

})(angular, app);

