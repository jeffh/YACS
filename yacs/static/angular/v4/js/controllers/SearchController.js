'use strict';

(function(angular, app, undefined){

app.service('searchOptions', ['$rootScope', function($rootScope){
	var defaults = {
		visible: true
	};
	var self = this;
	_.extend(self, defaults);

	$rootScope.$on('$routeChangeStart', function(){
		_.extend(self, defaults);
	});
}]);

app.controller('SearchCtrl', ['$scope', '$location', '$timeout', '$route', 'urlProvider',
			   'searchOptions', 'currentSemesterPromise',
			   function($scope, $location, $timeout, $route, urlProvider, searchOptions, currentSemesterPromise){
	var timeout = null;
	var previousPath = null;
	$scope.searchOptions = searchOptions;
	$scope.$watch('semester', function(semester){
		if (!semester) {
			return;
		}

		$scope.query = decodeURIComponent($route.current.params.query || '');
		$scope.$watch('query', function(){
			if (timeout){
				$timeout.cancel(timeout);
				timeout = null;
			}
			timeout = $timeout(function(){
				$scope.performSearch();
			}, 300);
		});

		$scope.performSearch = function(){
			if ($scope.query && $scope.query !== ''){
				// restore previous url
				if (!$route.current.params.query){
					previousPath = $location.path();
				}
				$location.path(urlProvider.search(
					semester.year,
					semester.month,
					$scope.query
				));
				timeout = null;
			} else if (previousPath){
				$location.path(previousPath);
			}
		};
	});
}]);

})(angular, app);

