'use strict';

(function(angular, app, undefined){

app.controller('RootCtrl', ['$scope', 'currentSemesterPromise',
			   'Selection', 'STATIC_URL', 'networkIndicator',
			   function($scope, currentSemesterPromise,
						Selection, STATIC_URL, networkIndicator){
	$scope.semester = currentSemesterPromise;
	$scope.STATIC_URL = STATIC_URL;
	$scope.networkIndicator = networkIndicator;

	Selection.current.then(function(selection){
		$scope.selection = selection;
	});
}]);

})(angular, app);

