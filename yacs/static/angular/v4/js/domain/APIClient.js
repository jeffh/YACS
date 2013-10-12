'use strict';

(function(angular, app, undefined){

app.value('apiClientCacheSize', 20);

var id = 0;
app.service('networkIndicator', ['$rootScope', function($rootScope){
	this.__ID = ++id;
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
	this.acquireFn = function(value){
		self.acquire();
		return value;
	};
	this.releaseFn = function(value){
		self.release();
		return value;
	};

	$rootScope.$on('$routeChangeStart', this.acquireFn);
	$rootScope.$on('$routeChangeSuccess', this.releaseFn);
	$rootScope.$on('$routeChangeError', this.releaseFn);
}]);

app.service('apiClient', ['$http', '$q', '$cacheFactory', '$rootScope',
			'Utils', 'apiClientCacheSize', 'networkIndicator', 'CSRF_TOKEN',
			function($http, $q, $cacheFactory, $rootScope, Utils,
					 apiClientCacheSize, networkIndicator, csrf_token){
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
			networkIndicator.release();
			deferred.resolve(response);
		} else {
			var promise = $http.post(url, params, {
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
					'X-CSRFToken': csrf_token
				}
			});
			promise.success(function(json, status, headers, config){
				networkIndicator.release();
				if (!json.success) {
					deferred.reject(new Error('Invalid server api response: success=false'), json || data);
					return;
				}
				deferred.resolve(json.result);
				cache.put(fullUrl, json.result);
			}).error(function(data, status, headers, config){
				networkIndicator.release();
				deferred.reject(new Error('Invalid server response: ' + status + '; '), data);
			});
		}

		return deferred.promise;
	};

	this.post = function(url, data){
		networkIndicator.acquire();
		data = $.param(data || {});
		var deferred = $q.defer();

		var promise = $http.post(url, data, {
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
		});
		promise.success(function(json, status, headers, config){
			networkIndicator.release();
			if (!json.success) {
				deferred.reject(new Error('Invalid server api response: success=false'), json || data);
				return;
			}
			deferred.resolve(json.result);
		}).error(function(data, status, headers, config){
			networkIndicator.release();
			deferred.reject(new Error('Invalid server response: ' + status + '; '), data);
		});

		return deferred.promise;
	};
}]);

})(angular, app);

