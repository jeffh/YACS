'use strict';

(function(angular, app, undefined){

app.factory('tagger', function(kSectionTimeTags, kCourseTags){
	return function (section){
		var tags = [];
		_(section.sectionTypes()).each(function(type){
			if (kSectionTimeTags[type]){
				tags.push(kSectionTimeTags[type]);
			} else if (type && type !== '') {
				tags.push({name: type, sort_order: 9999});
			}
		});

		if (section.is_comm_intense) {
			tags.push(kCourseTags.communicationIntensive);
		}
		if (section.grade_type === 'Satisfactory/Unsatisfactory') {
			tags.push(kCourseTags.passOrFail);
		}

		// TODO: prereq & crosslist
		return _.sortBy(tags, 'sort_order');
	};
});

})(angular, app);

