'use strict';
(function(window, angular){
window.app = angular.module('yacs', []);

app.factory('urlProvider', function(){
    return function(){
        var args = _.toArray(arguments);
        if (args.length) {
            console.log(args);
            console.trace();
            return '/' + args.join('/') + '/';
        }
        return '/';
    };
});

app.config(['$routeProvider', function($routeProvider){
    $routeProvider.when('/:year/:month/', {
        templateUrl: '/static/v4/partials/departments.html',
        controller: 'DeptCtrl'
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

})(window, angular);
