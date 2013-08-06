'use strict';

(function(window, angular){

window.app = angular.module('yacs', ['ngCookies']);

app.service('urlProvider', function(){
	function url(){
		var args = _(arguments).map(function(arg){
			return encodeURIComponent(arg);
		});
		if (args.length) {
			return '/' + args.join('/') + '/';
		}
		return '/';
	};

	this.semester = function(year, month){
		return url('semesters', year, month);
	};

	this.selected = function(year, month){
		return url('semesters', year, month, 'selected');
	};

	this.search = function(year, month, query){
		return url('semesters', year, month, 'search', query);
	};

	this.department = function(year, month, deptcode){
		return url('semesters', year, month, deptcode.toUpperCase());
	};
});

app.config(['$routeProvider', 'STATIC_URL', function($routeProvider, STATIC_URL){
	$routeProvider.when('/semesters/:year/:month/', {
		templateUrl: STATIC_URL + 'v4/partials/departments.html',
		controller: 'DepartmentCtrl'
	});
	$routeProvider.when('/semesters/:year/:month/selected/', {
		templateUrl: STATIC_URL + 'v4/partials/selection.html',
		controller: 'SelectionCtrl',
		reloadOnSearch: false
	});
	$routeProvider.when('/semesters/:year/:month/search/:query/', {
		templateUrl: STATIC_URL + 'v4/partials/catalog.html',
		controller: 'SearchResultsCtrl'
	});
	$routeProvider.when('/semesters/:year/:month/:dept/', {
		templateUrl: STATIC_URL + 'v4/partials/catalog.html',
		controller: 'CatalogCtrl'
	});
	$routeProvider.when('/', {
		templateUrl: STATIC_URL + 'v4/partials/departments.html',
		controller: 'IndexCtrl'
	});
}]);

app.config(['$locationProvider', function($locationProvider){
	$locationProvider.html5Mode(false);
}]);

})(window, angular);
