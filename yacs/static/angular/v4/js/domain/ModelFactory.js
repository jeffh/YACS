'use strict';

(function(angular, app, undefined){

app.factory('ModelFactory', function(apiClient){
	var callOrReturn = function(fn, args){
		if (angular.isFunction(fn)){
			return fn.apply(window, args);
		}
		return fn;
	};
	return function(name, options){
		options = options || {};
		// yes, we eval to get nice pretty debugging output names
		var Model = eval('(function ' + name + '(){ this.initialize.apply(this, arguments); })');
		Model.prototype = {};

		angular.extend(Model, {
			query: function(filters){
				filters = filters || {};
				var promise = apiClient.get(callOrReturn(options.query, [filters]), filters);
				return promise.then(function(result){
					var collection = [];
					for (var i=0; i<result.length; i++) {
						collection.push(new Model(result[i]));
					}
					return collection;
				});
			},
			get: function(id) {
				var promise = apiClient.get(callOrReturn(options.get, [id]));
				return promise.then(function(result){
					return new Model(result);
				});
			}
		});

		angular.extend(Model.prototype, {
			initialize: function(attributes){
				var defaults = options.defaults || {};
				this.__attributes__ = _.union(_.keys(defaults), _.keys(attributes || {}));
				angular.extend(this, angular.copy(defaults), attributes);
			},
			refresh: function(){
				var self = this;
				var promise = apiClient.get(callOrReturn(options.get, [self.id]));
				return promise.then(function(result){
					angular.extend(self, result);
					return self;
				});
			},
			equals: function(model){
				return this.id === model.id;
			},
			toObject: function(){
				var obj = {}, self = this;
				_.each(this.__attributes__, function(attr){
					obj[attr] = self[attr];
				});
				return obj;
			}
		});

		return Model;
	};
});

})(angular, app);

