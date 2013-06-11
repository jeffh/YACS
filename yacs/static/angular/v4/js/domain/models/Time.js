'use strict';

(function(angular, app, undefined){

app.factory('Time', function(){
	function Time(str){
		var parts = _(str.split(':')).map(function(i){ return parseInt(i, 10); });
		this.hour = parts[0];
		this.minute = parts[1];
		this.second = parts[2];
		this.totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
	}
	Time.prototype = {};
	angular.extend(Time.prototype, {
		isOnTheHour: function(){
			return this.minute === 0 && this.second === 0;
		},
		isAM: function(){
			return this.hour < 12;
		},
		APM: function(){
			return (this.isAM() ? 'am' : 'pm');
		},
		getLocalHour: function(){
			var hour = this.hour;
			if (hour == 0 || hour == 12) {
				return 12;
			}
			return (hour > 12 ? hour - 12 : hour);
		},
		text: function(options){
			options = _.extend({
				showAPM: true
			}, options);

			var times = [];
			times.push(this.getLocalHour());
			if (!this.isOnTheHour()){
				times.push(':');
				times.push(this.minute);
			}
			if (options.showAPM) {
				times.push(this.APM());
			}
			return times.join('');
		}
	});
	return Time;
});

})(angular, app);

