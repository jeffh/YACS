'use strict';

(function(angular, app, undefined){

app.factory('Conflict', ['ModelFactory', 'Utils', function(ModelFactory, Utils){
	var url = Utils.URL('/api/4/conflicts/');
	/*
	 * id: 1
	 * conflicts: []
	 */
	var Conflict = ModelFactory('Conflict', {
		get: url,
		query: url
	});
	angular.extend(Conflict.prototype, {
		conflictsWith: function(id){
			return _.contains(this.conflicts, id);
		}
	});
	return Conflict;
}]);

})(angular, app);

