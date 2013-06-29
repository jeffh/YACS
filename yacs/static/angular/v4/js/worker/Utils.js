'use strict';

// requires underscore
// requires AppWorker.Namespace
AppWorker.Utils = {
	hashById: function(items, property){
		var result = {};
		property = property || 'id';
		_(items).each(function(item){
			result[item[property]] = item;
		});
		return result;
	},
	altProduct: function(domains){
		function cartProduct(index){
			if (index === domains.length) {
				return [[]];
			} else {
				var results = [];
				_.each(domains[index], function(item){
					_.each(cartProduct(index + 1), function(result){
						result.push(item);
						results.push(result);
					});
				});
				return results;
			}
		}
		return cartProduct(0);
	},
	product: function(domains){
		var result = [[]];
		_(domains).each(function(domain){
			var tmp = [];
			_(result).each(function(accum){
				_(domain).map(function(value){
					var newAccum = accum.slice();
					newAccum.push(value);
					tmp.push(newAccum);
				});
			});
			result = tmp;
		});
		return result;
	}
};

