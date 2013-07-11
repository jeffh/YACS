'use strict';

(function(angular, app, undefined){

app.controller('IndexCtrl', ['$scope', '$location', 'currentSemesterPromise', 'urlProvider',
			   function($scope, $location, currentSemesterPromise, urlProvider) {
	currentSemesterPromise.then(function(semester){
		$location.path(urlProvider(semester.year, semester.month));
	});
}]);

})(angular, app);

