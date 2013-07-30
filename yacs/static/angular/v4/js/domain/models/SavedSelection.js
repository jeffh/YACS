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
		 get: url,
		 save: url,
		 serialize: function(){
			 return {
				 section_ids: _.values(this.selection).join(','),
				 blocked_times: _.keys(this.blocked_times).join(',')
			 };
		 }
	 });
	 window.SavedSelection = SavedSelection;

	 return SavedSelection;
}]);

})(angular, app);

