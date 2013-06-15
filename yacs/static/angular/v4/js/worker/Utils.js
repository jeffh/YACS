'use strict';

// requires underscore
// requires Worker.Namespace
Worker.Utils = {
	hashById: function(items, property){
		var result = {};
		property = property || 'id';
		_(items).each(function(item){
			result[item[property]] = item;
		});
		return result;
	},
	product: function(domains){
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
	}
};

