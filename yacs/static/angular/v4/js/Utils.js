'use strict';

(function(angular, app, undefined){

app.service('Utils', function(){
	_.extend(this, AppWorker.Utils);

	this.pluralize = function(word, num){
		return (num === 1) ? word : word + 's';
	};

	this.URL = function(baseUrl){
		return function(id){
			return angular.isNumber(id) ? baseUrl + id : baseUrl;
		}
	};

    this.queryString = function(params){
		var sb = [];
		angular.forEach(params, function(value, key){
			if (!angular.isArray(value)){
				value = [value];
			}
			angular.forEach(value, function(v){
				sb.push(key + '=' + v);
			});
		});
		return sb.join('&');
    };
});

})(angular, app);

