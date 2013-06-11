'use strict';

(function(angular, app, undefined){

app.factory('CourseSearch', function(){
	var contains = function(string, substring){
		return string.indexOf(substring) >= 0;
	};
	return function(courses, query){
		var words = _.compact(query.toLowerCase().split(' '));
		return _(courses).filter(function(course){
			var courseName = course.name.toLowerCase();
			var deptCode = course.department.code.toLowerCase();
			return _.every(words, function(word){
				return (
					contains(courseName, word) ||
					contains(deptCode, word) ||
					contains(String(course.number), word)
				);
			});
		});
	};
});

})(angular, app);

