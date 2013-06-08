'use strict';

(function(document, angular, app, undefined){

app.controller('RootCtrl', function($scope, currentSemesterPromise, Selection){
	$scope.semester = currentSemesterPromise;
	Selection.current.then(function(selection){
		$scope.selection = selection;
	});
});

app.controller('FooterCtrl', function($scope){
	var choices = [
		'A grass-fed, free-ranged',
		'The best',
		'Yet another',
		"An experimental, GMO'd",
		'A radioactive',
		'A zombie',
		'An',
		'A pizza-funded',
		'An ice tea powered',
		'A lone computer runs this',
		"Some guy's",
		'A (somewhat) tested',
		'Batteries not included in this',
	];
	var index = Math.floor(Math.random() * choices.length);
	$scope.flavorText = choices[index];
});

app.controller('NavCtrl', function($scope, $location, urlProvider){
	$scope.semester.then(function(semester){
		var previousPath = null;
		var catalogItem = {
			name: 'Catalog',
			path: function(){
				if (previousPath){
					var oldPath = previousPath;
					previousPath = null;
					return oldPath;
				}
				return urlProvider(semester.year, semester.month);
			}
		};
		var selectedItem = {
			name: 'Selected',
			path: function(){
				previousPath = $location.path();
				return urlProvider(semester.year, semester.month, 'selected');
			}
		};

		$scope.$watch('selection', function(selection){
			if (selection){
				selectedItem.name = 'Selected (' + selection.numberOfCourses() + ')';
			}
		}, true);

		$scope.items = [catalogItem, selectedItem];
		$scope.selectedItem = catalogItem;
		_($scope.items).each(function(item){
			if ($location.path() === item.path()){
				$scope.selectedItem = item;
			}
		});
		previousPath = null;

		$scope.click = function(item){
			$scope.selectedItem = item;
			$location.path(item.path());
		};
	});
});

app.controller('SearchCtrl', function($scope, $location, $timeout, $route, urlProvider){
	var timeout = null;
	var previousPath = null;
	$scope.semester.then(function(semester){
		$scope.query = decodeURIComponent($route.current.params.query || '');
		$scope.$watch('query', function(){
			if (timeout){
				$timeout.cancel(timeout);
				timeout = null;
			}
			timeout = $timeout(function(){
				if ($scope.query && $scope.query !== ''){
					// restore previous url
					if (!$route.current.params.query){
						previousPath = $location.path();
					}
					$location.path(urlProvider(
						semester.year,
						semester.month,
						'search',
						$scope.query
					));
					timeout = null;
				} else if (previousPath){
					$location.path(previousPath);
				} else {
					$location.path(urlProvider(semester.year, semester.month));
				}
			}, 250);
		});
	});
});

app.controller('SearchResultsCtrl', function($scope, $routeParams, $location, CourseFetcher, CourseSearch, urlProvider){
	$scope.courses = [];
	var query = decodeURIComponent($routeParams.query || '');
	$scope.semester.then(function(semester){
		if (query == '') {
			return;
		}
		CourseFetcher({semester_id: semester.id}).then(function(allCourses){
			$scope.courses = CourseSearch(allCourses, $routeParams.query);
		});
	});
});

app.controller('DeptCtrl', function($scope, $location, Semester, Department, urlProvider, currentSemesterPromise){
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
});

app.controller('CatalogCtrl', function($q, $scope, $location, $routeParams, $timeout, CourseFetcher, Selection){
	$scope.courses = [];
	var selectionPromise = Selection.current;
	$scope.semester.then(function(semester){
		var coursePromise = CourseFetcher({semester_id: semester.id, department_code: $routeParams.dept.toUpperCase()});
		$q.all([selectionPromise, coursePromise]).then(function(values){
			var selection = values[0];
			var courses = values[1];
			window.selection = selection;
			$scope.courses = courses;
			selection.apply(courses);
		});
	});

	$scope.click_course = function(course){
		selectionPromise.then(function(selection){
			selection.updateCourse(course).then(function(){
				selection.save();
				selection.apply($scope.courses);
			}, function(err){
				selection.apply($scope.courses);
			});
		});
	};

	$scope.click_section = function(course, section){
		selectionPromise.then(function(selection){
			selection.updateSection(course, section).then(function(){
				selection.save();
				selection.apply($scope.courses);
			}, function(err){
				selection.apply($scope.courses);
			});
		});
	};
});

app.controller('IndexCtrl', function($scope, $location, $route, Semester, urlProvider) {
	Semester.latest().then(function(semester){
		$location.path(urlProvider(semester.year, semester.month));
	});
});

app.controller('SelectionCtrl', function($scope){
});

})(document, angular, app);

