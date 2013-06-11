'use strict';

(function(angular, app, undefined){

app.controller('RootCtrl', function($scope, currentSemesterPromise, Selection){
	$scope.semester = currentSemesterPromise;
	Selection.current.then(function(selection){
		$scope.selection = selection;
	});
});

})(angular, app);

