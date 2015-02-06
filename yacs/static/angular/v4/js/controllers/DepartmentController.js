'use strict';

(function(angular, app, undefined){

app.controller('DepartmentCtrl', ['$scope', '$location', 'Semester',
			   'Department', 'urlProvider',
			   function($scope, $location, Semester, Department, urlProvider){
	$scope.departments = [];

	$scope.$watch('semester', function(semester){
		Department.query({semester_id: semester.id}).then(function(departments){
			$scope.departments = departments;
		});
		$scope.click = function(dept){
			$location.path(urlProvider.department(
				semester.year,
				semester.month,
				dept.code
			));
		};
	});
}]);

})(angular, app);

