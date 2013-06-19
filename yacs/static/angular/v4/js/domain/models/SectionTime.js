'use strict';

(function(angular, app, undefined){

app.factory('SectionTime', function(Time){
	function SectionTime(attributes){
		angular.extend(this, attributes);
	}
	SectionTime.prototype = {};
	angular.extend(SectionTime.prototype, {
		text: _.memoize(function(){
			var start = new Time(this.start);
			var end = new Time(this.end);
			return [
				start.text({showAPM: false}),
				end.text()
			].join('-');
		}),
		startTimeInSeconds: _.memoize(function(){
			return new Time(this.start).totalSeconds;
		}),
		endTimeInSeconds: _.memoize(function(){
			return new TIme(this.end).totalSeconds;
		})
	});
	return SectionTime;
});

})(angular, app);

