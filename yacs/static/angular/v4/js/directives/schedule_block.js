'use strict';

(function(angular, app, $, undefined){

app.constant('hourBlockSize', 26.0 * 2);
app.constant('blockStartingOffset', 1);

app.directive('yacsBlockOffset', function($parse, hourBlockSize, blockStartingOffset){
	return function(scope, element, attrs){
		function update(){
			var startHour = parseFloat($parse(attrs.yacsBlockOffset)(scope));
			element.css({top: startHour * hourBlockSize + blockStartingOffset});
		}

		scope.$watch(attrs.yacsBlockOffset, function(){
			update();
		});
	};
});

app.directive('yacsBlockHeight', function($parse, hourBlockSize, blockStartingOffset){
	return function(scope, element, attrs){
		function update(){
			var durationInSeconds = parseFloat($parse(attrs.yacsBlockHeight)(scope));
			element.css({height: durationInSeconds / 3600.0 * hourBlockSize - blockStartingOffset});
		}

		scope.$watch(attrs.yacsBlockOffset, function(){
			update();
		});
	};
});

app.directive('yacsKeydown', function($parse){
	return function(scope, element, attrs){
		$(document).on('keydown', function(evt){
			scope.$apply(function(){
				$parse(attrs.yacsKeydown)(scope, {$event: evt});
			});
		});
	};
});

})(angular, app, jQuery);

