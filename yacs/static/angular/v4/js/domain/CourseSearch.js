'use strict';

(function(angular, app, undefined){

app.factory('CourseSearch', function(){
	// score bonus for field matching
	var nameScore = 200,
		deptScore = 100,
		numberScore = 75,
		instructorScore = 50;
	// score modifiers
	var beginningBonusMultiplier = 10,
		shortSubstringMaxScore = 1;
	
	// "not a match" if less than this
	var cutoffScore = 50;

	var matches = function(string, substring, scoreBonus){
		var index = string.indexOf(substring);
		if (index >= 0 && substring.length < 3){
			return shortSubstringMaxScore;
		} else if (index === 0){
			return beginningBonusMultiplier * scoreBonus;
		} else if (index > 0){
			return scoreBonus;
		} else {
			return 0;
		}
	};


	return function(courses, query){
		var words = _.compact(query.toLowerCase().split(' '));
		return _(courses).chain().map(function(course){
			var courseName = course.name.toLowerCase();
			var deptCode = course.department.code.toLowerCase();
			var instructors = course.instructors().join(' ').toLowerCase();
			var score = _.reduce(words, function(accum, word){
				var additiveScore = (
					matches(courseName, word, nameScore) +
					matches(deptCode, word, deptScore) +
					matches(String(course.number), word, numberScore) +
					matches(instructors, word, instructorScore)
				);
				if (additiveScore > 0){
					return accum + additiveScore;
				} else {
					return 0;
				}
			}, 0);
			course.score = score;
			return course;
		}).filter(function(course){
			return course.score >= cutoffScore;
		}).sortBy(function(course){
			return -course.score; // DESC
		}).value();
	};
});

})(angular, app);

