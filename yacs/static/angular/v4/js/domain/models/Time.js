'use strict';

(function(angular, app, undefined){

app.factory('Time', function(){
	function Time(hour, minute, second){
		this.hour = parseInt(hour || 0, 10);
		this.minute = parseInt(minute || 0, 10);
		this.second = parseInt(second || 0, 10);
		this.totalSeconds = this.hour * 3600 + this.minute * 60 + this.second;
	}
	Time.parse = function(str){
		var parts = str.split(':');
		return new Time(parts[0], parts[1], parts[2]);
	};
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
		shortText: function(options){
			var localHour = this.getLocalHour();
			if (localHour === 12){
				return 'Noon';
			} else {
				return localHour;
			}
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
		},
		toObject: function(){
			return [this.hour, this.minute, this.second].join(':');
		}
	});
	return Time;
});

})(angular, app);

