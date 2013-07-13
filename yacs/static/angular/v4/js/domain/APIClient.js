'use strict';

(function(angular, app, undefined){

app.value('apiClientCacheSize', 20);

app.service('networkIndicator', function($rootScope){
	var networkCount = 0;
	this.isVisible = function(){
		return networkCount > 0;
	};
	this.acquire = function(){
		networkCount++;
	};
	this.release = function(){
		networkCount = Math.max(0, networkCount - 1);
	};
	var self = this;

	$rootScope.$watch('$routeChangeStart', function(){
		networkCount = 0;
		self.acquire();
	});
	$rootScope.$watch('$routeChangeSuccess', function(){
		self.release();
	});
	$rootScope.$watch('$routeChangeError', function(){
		self.release();
	});
});

app.service('apiClient', ['$http', '$q', '$cacheFactory',
			'Utils', 'apiClientCacheSize', 'networkIndicator',
			function($http, $q, $cacheFactory, Utils,
					 apiClientCacheSize, networkIndicator){
	var cache = $cacheFactory('apiCache', {number: apiClientCacheSize});
	this.get = function(url, params){
		networkIndicator.acquire();
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

		return deferred.promise.then(function(result){
			networkIndicator.release();
			return result;
		}, function(err){
			networkIndicator.release();
			return err;
		});
	};
}]);

})(angular, app);

