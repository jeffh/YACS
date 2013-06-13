'use strict';

(function(angular, app, undefined){

app.controller('RootCtrl', function($scope, currentSemesterPromise, Selection, STATIC_URL){
	$scope.semester = currentSemesterPromise;
	$scope.STATIC_URL = STATIC_URL;
	Selection.current.then(function(selection){
		$scope.selection = selection;
	});
});

})(angular, app);

