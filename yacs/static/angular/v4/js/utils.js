'use strict';

(function(document, angular, app, undefined){

app.service('Utils', function(){
	this.pluralize = function(word, num){
		return (num === 1) ? word : word + 's';
	};

	this.hashById = function(items, property){
		var result = {};
		property = property || 'id';
		_(items).each(function(item){
			result[item[property]] = item;
		});
		return result;
	};

	this.product = function(domains){
		var result = [[]];
		_(domains).each(function(domain){
			var tmp = [];
			_(result).each(function(accum){
				_(domain).map(function(value){
					var newAccum = angular.copy(accum);
					newAccum.push(value);
					tmp.push(newAccum);
				});
			});
			result = tmp;
		});
		return result;
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

})(document, angular, app);

