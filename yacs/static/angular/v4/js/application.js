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

app.config(['$routeProvider', function($routeProvider){
    $routeProvider.when('/:year/:month/', {
        templateUrl: '/static/v4/partials/departments.html',
        controller: 'DepartmentCtrl'
    });
    $routeProvider.when('/:year/:month/selected/', {
        templateUrl: '/static/v4/partials/courses.html',
        controller: 'SelectionCtrl'
    });
    $routeProvider.when('/:year/:month/search/:query/', {
        templateUrl: '/static/v4/partials/courses.html',
        controller: 'SearchResultsCtrl'
    });
    $routeProvider.when('/:year/:month/:dept/', {
        templateUrl: '/static/v4/partials/courses.html',
        controller: 'CatalogCtrl'
    });
    $routeProvider.when('/', {
        templateUrl: '/static/v4/partials/departments.html',
        controller: 'IndexCtrl'
    });
}]);

app.config(['$locationProvider', function($locationProvider){
    $locationProvider.html5Mode(false);
}]);

})(window, angular);
