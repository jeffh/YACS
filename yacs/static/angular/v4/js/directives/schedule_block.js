'use strict';

(function(angular, app, $, undefined){

app.constant('hourBlockSize', 52.0);
app.constant('blockStartingOffset', 1.0);

app.directive('yacsFocus', ['$parse', function($parse){
	return function(scope, element, attrs){
		return element.on('focus', function(evt){
			$parse(attrs.yacsFocus)(scope, {$event: evt});
		});
	};
}]);

app.directive('yacsStopEvent', function(){
	return {
		restrict: 'A',
		link: function(scope, element, attrs){
			element.on(attrs.yacsStopEvent, function(evt){
				evt.stopPropagation();
			})
		}
	};
});

app.directive('yacsBlockOffset', ['$parse', 'hourBlockSize', 'blockStartingOffset',
			  function($parse, hourBlockSize, blockStartingOffset){
	return function(scope, element, attrs){
		function update(){
			var startHour = parseFloat($parse(attrs.yacsBlockOffset)(scope));
			element.css({top: startHour * hourBlockSize + blockStartingOffset});
		}

		scope.$watch(attrs.yacsBlockOffset, function(){
			update();
		});
	};
}]);

app.directive('yacsBlockHeight', ['$parse', 'hourBlockSize', 'blockStartingOffset',
			  function($parse, hourBlockSize, blockStartingOffset){
	return function(scope, element, attrs){
		function update(){
			var durationInSeconds = parseFloat($parse(attrs.yacsBlockHeight)(scope));
			element.css({height: durationInSeconds / 3600.0 * hourBlockSize - blockStartingOffset});
		}

		scope.$watch(attrs.yacsBlockOffset, function(){
			update();
		});
	};
}]);

app.directive('yacsKeydown', ['$parse', function($parse){
	return function(scope, element, attrs){
		$(document).on('keydown', function(evt){
			scope.$apply(function(){
				$parse(attrs.yacsKeydown)(scope, {$event: evt});
			});
		});
	};
}]);

})(angular, app, jQuery);

