'use strict';

(function(angular, app, undefined){

app.factory('SectionTime', function(Time){
	function SectionTime(attributes){
		angular.extend(this, attributes);
	}
	SectionTime.prototype = {};
	angular.extend(SectionTime.prototype, {
		text: function(){
			var start = new Time(this.start);
			var end = new Time(this.end);
			return [
				start.text({showAPM: false}),
				end.text()
			].join('-');
		},
		startTimeInSeconds: function(){
			return new Time(this.start).totalSeconds;
		},
		endTimeInSeconds: function(){
			return new TIme(this.end).totalSeconds;
		}
	});
	return SectionTime;
});

})(angular, app);

