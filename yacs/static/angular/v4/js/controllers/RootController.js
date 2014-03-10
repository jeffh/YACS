'use strict';

(function(angular, app, undefined){

app.controller('RootCtrl', ['$scope', 'currentSemesterPromise',
			   'Selection', 'STATIC_URL', 'networkIndicator',
			   function($scope, currentSemesterPromise,
						Selection, STATIC_URL, networkIndicator){
	$scope.STATIC_URL = STATIC_URL;
	$scope.networkIndicator = networkIndicator;

	currentSemesterPromise.then(function(semester){
		$scope.semester = semester;
	});

	Selection.current.then(function(selection){
		$scope.selection = selection;
	});
}]);

})(angular, app);

