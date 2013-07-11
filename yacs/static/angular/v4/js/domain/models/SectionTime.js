'use strict';

(function(angular, app, undefined){

app.factory('SectionTime', ['Time', function(Time){
	function SectionTime(attributes){
		angular.extend(this, attributes);
		this.start_time = Time.parse(this.start || '0:00:00');
		this.end_time = Time.parse(this.end || '0:00:00');
		this.__text = null;
	}
	SectionTime.prototype = {};
	angular.extend(SectionTime.prototype, {
		text: function(){
			if (!this.__text){
				this.__text = [
					this.start_time.text({showAPM: false}),
					this.end_time.text()
				].join('-');
			}
			return this.__text;
		},
		startTimeInSeconds: function(){
			return this.start_time.totalSeconds;
		},
		endTimeInSeconds: function(){
			return this.end_time.totalSeconds;
		},
		toObject: function(){
			return {
				days_of_the_week: this.days_of_the_week,
				start: this.start_time.toObject(),
				end: this.end_time.toObject()
			};
		}
	});
	return SectionTime;
}]);

})(angular, app);

