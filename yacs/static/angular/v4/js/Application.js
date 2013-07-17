'use strict';

(function(window, angular){

window.app = angular.module('yacs', ['ngCookies']);

app.factory('urlProvider', function(){
	return function(){
		var args = _(arguments).map(function(arg){
			return encodeURIComponent(arg);
		});
		if (args.length) {
			return '/' + args.join('/') + '/';
		}
		return '/';
	};
});

app.config(['$routeProvider', 'STATIC_URL', function($routeProvider, STATIC_URL){
	$routeProvider.when('/:year/:month/', {
		templateUrl: STATIC_URL + 'v4/partials/departments.html',
		controller: 'DepartmentCtrl'
	});
	$routeProvider.when('/:year/:month/selected/', {
		templateUrl: STATIC_URL + 'v4/partials/selection.html',
		controller: 'SelectionCtrl',
		reloadOnSearch: false
	});
	$routeProvider.when('/:year/:month/search/:query/', {
		templateUrl: STATIC_URL + 'v4/partials/catalog.html',
		controller: 'SearchResultsCtrl'
	});
	$routeProvider.when('/:year/:month/:dept/', {
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
