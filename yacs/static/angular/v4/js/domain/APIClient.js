'use strict';

(function(angular, app, undefined){

app.value('apiClientCacheSize', 20);

app.service('apiClient', function($http, $q, $cacheFactory, Utils, apiClientCacheSize){
	var cache = $cacheFactory('apiCache', {number: apiClientCacheSize});
	this.get = function(url, params){
		params = params || {};
		var fullUrl = url;
		if (!_.isEmpty(params)){
			fullUrl += '?' + Utils.queryString(params);
		}
		var deferred = $q.defer();

		var response = cache.get(fullUrl);
		if (response){
			deferred.resolve(response);
		} else {
			var promise = $http.get(fullUrl);
			promise.success(function(json, status, headers, config){
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
	};
});

})(angular, app);

