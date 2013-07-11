'use strict';

(function(angular, app, undefined){

app.factory('DelayTrigger', ['$timeout', function($timeout){
	return function(fn, timeout){
		var timer = null;
		return function(){
			if (timer){
				$timeout.cancel(timer);
				timer = null;
			}
			timer = $timeout(function(){
				timer = null;
				fn();
			}, timeout);
		};
	};
}]);

})(angular, app);

