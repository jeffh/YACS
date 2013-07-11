'use strict';

(function(angular, app, undefined){

app.controller('FooterCtrl', ['$scope', function($scope){
	var choices = [
		'A grass-fed, free-ranged',
		'The best',
		'Yet another',
		"An experimental, GMO'd",
		'A radioactive',
		'A zombie',
		'An',
		'A pizza-funded',
		'An ice tea powered',
		'A lone computer runs this',
		"Some guy's",
		'A (somewhat) tested',
		'Batteries not included in this'
	];
	var index = Math.floor(Math.random() * choices.length);
	$scope.flavorText = choices[index];
}]);

})(angular, app);
