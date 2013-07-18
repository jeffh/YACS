'use strict';

(function(angular, app, undefined){

app.factory('SavedSelection', ['Utils', 'ModelFactory',
			function(Utils, ModelFactory){
	var url = Utils.URL('/api/4/selections/');
	/*
	 * id: 1
	 * selection: {courseId: sectionIds}
	 * blocked_times: [(startInSeconds, endInSeconds)...]
	 */
	 var SavedSelection = ModelFactory('SavedSelection', {
		 query: url,
		 get: url
	 });

	 return Course;
}]);

})(angular, app);

