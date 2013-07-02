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
	flatten: function(linkedList){ 
		var result = [];
		var tail = linkedList;
		while (tail.last){
			result.unshift(tail.last);
			tail = tail.rest;
		}
		return result;
	},
	product: function(domains){
		var result = [[]];
		_(domains).each(function(domain){
			var tmp = [];
			_(result).each(function(accum){
				_(domain).map(function(value){
					var newAccum = {rest: accum, last: value};
					tmp.push(newAccum);
				});
			});
			result = tmp;
		});
		return _.map(result, AppWorker.Utils.flatten);
	}
};

