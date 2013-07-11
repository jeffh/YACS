'use strict';

(function(angular, app, undefined){

app.factory('Department', ['ModelFactory', 'Utils',
			function(ModelFactory, Utils){
	var url = Utils.URL('/api/4/departments/');
	/*
	 * code: "ADMN",
	 * id: 38,
	 * name: "Administration"
	 */
	var Department = ModelFactory('Department', {
		query: url,
		get: url
	});
	return Department;
}]);

})(angular, app);

