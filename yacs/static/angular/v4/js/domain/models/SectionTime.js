'use strict';

(function(angular, app, undefined){

app.factory('SectionTime', function(Time){
	function SectionTime(attributes){
		angular.extend(this, attributes);
		this.start_time = Time.parse(this.start);
		this.end_time = Time.parse(this.end);
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
		}
	});
	return SectionTime;
});

})(angular, app);

