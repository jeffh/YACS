'use strict';

(function(angular, app, undefined){

app.service('Utils', function(){
	_.extend(this, AppWorker.Utils);

	this.pluralize = function(word, num){
		return (num === 1) ? word : word + 's';
	};

	this.URL = function(baseUrl){
		return function(id){
			if (angular.isNumber(id) || !isNaN(parseInt(id, 10))) {
				return baseUrl + id;
			}
			return baseUrl;
		}
	};

    this.queryString = function(params){
		var sb = [];
		angular.forEach(params, function(value, key){
			if (!angular.isArray(value)){
				value = [value];
			}
			sb.push(key + '=' + value.join(','));
		});
		return sb.join('&');
    };
});

})(angular, app);

