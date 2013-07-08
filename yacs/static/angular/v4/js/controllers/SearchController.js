'use strict';

(function(angular, app, undefined){

app.service('searchOptions', function($rootScope){
	var defaults = {
		visible: true
	};
	var self = this;
	_.extend(self, defaults);

	$rootScope.$on('$routeChangeStart', function(){
		_.extend(self, defaults);
	});
});

app.controller('SearchCtrl', function($scope, $location, $timeout, $route, urlProvider, searchOptions){
	var timeout = null;
	var previousPath = null;
	$scope.searchOptions = searchOptions;
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
				}
			}, 1000);
		});
	});
});

})(angular, app);

