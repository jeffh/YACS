'use strict';

(function(document, angular, app, undefined){

var Error = app.Error = function(msg, info){
	this.msg = msg;
	this.info = info;
	this.isError = true;
};

app.service('apiClient', function($http, $q, $cacheFactory){
	var cache = $cacheFactory('apiCache', {number: 20});
	var parameters = function(params){
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
	return {
		clearCache: function(){
			cache.removeAll();
		},
		get: function(url, params){
			params = params || {};
			var fullUrl = url + '?' + parameters(params);
			var deferred = $q.defer();
			var key = fullUrl;

			var response = cache.get(fullUrl);
			if (response){
				deferred.resolve(response);
			} else {
				var promise = $http.get(fullUrl);
				promise.success(function(data, status, headers, config){
					var json = angular.fromJson(data);
					if (status < 200 || status >= 300) {
						deferred.reject(new Error('Invalid server response: ' + status + '; '), json || data);
						return;
					}
					if (!json.success) {
						deferred.reject(new Error('Invalid server api response: success=false'), json || data);
						return;
					}
					deferred.resolve(json.result);
					cache.put(fullUrl, json.result);
				}).error(function(data, status, headers, config){
					deferred.reject(new Error('Invalid server response: ' + status + '; '), data);
				});
			}

			return deferred.promise;
		}
	};
});


})(window, angular, app);

