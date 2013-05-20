'use strict';

(function(document, angular, app, undefined){

app.controller('RootCtrl', function($scope, Semester, Department){
	$scope.semester = Semester.latest();
	$scope.selectedCourses = [];
});

app.controller('NavCtrl', function($scope){
	$scope.items = [
		{name: 'Search', id: 'search'},
		{name: 'Departments', id: 'department'}
	];
	$scope.selectedItem = $scope.items[1];

	$scope.itemClass = function(item){
		if (item.id == $scope.selectItem.id) {
			return 'selected';
		}
		return '';
	};

	$scope.click = function(item){
		console.log('clicked', item);
	};
});

app.controller('SearchCtrl', function($scope, Course){
	$scope.query = '';

	var courses = [];
	Course.query({semester: $scope.semester.id}).then(function(allCourses){
		courses = allCourses;
	});
});

app.controller('DeptCtrl', function($scope, $location, Department, urlProvider){
	$scope.departments = [];
	var sem = null;

	$scope.semester.then(function(semester){
		sem = semester;
		$scope.departments = Department.query({semester_id: semester.id});
	});

	$scope.click = function(dept){
		$location.path(urlProvider(
			sem.year,
			sem.month,
			dept.code
		));
	};
});

var hashById = function(items, property){
	var result = {}
	property = property || 'id';
	angular.forEach(items, function(item){
		result[item[property]] = item;
	});
	return result;
};

app.controller('CatalogCtrl', function($q, $scope, $location, $routeParams, $timeout, Course, Section, Department){
	$scope.courses = [];

	var fetchCourses = function(semester, idToDept) {
		var filters = {semester_id: semester.id};
		if ($routeParams.dept){
			filters.department_code = $routeParams.dept.toUpperCase();
		}
		$scope.courses = Course.query(filters);
		$scope.courses.then(function(courses){
			var idToCourse = hashById(courses);
			var courseIds = _.keys(idToCourse);
			_(courses).each(function(course){
				course.sections = [];
				course.department = idToDept[course.department_id];
			});
			Section.query({course_id: courseIds, semester_id: semester.id}).then(function(sections){
				_(sections).each(function(section){
					idToCourse[section.course_id].sections.push(section);
				});
				_(courses).each(function(course){
					course.tags = course.generateTags();
				});
			});
		});
	};

	$scope.semester.then(function(semester){
		Department.query({semester_id: semester.id}).then(function(departments){
			var idToDept = hashById(departments);
			fetchCourses(semester, idToDept);
		});
	});
});

app.controller('IndexCtrl', function($scope, $location, Semester, urlProvider) {
	Semester.latest().then(function(semester){
		$location.path(urlProvider(semester.year, semester.month));
	});
});

})(document, angular, app);

