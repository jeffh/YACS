'use strict';

(function(angular, app, undefined){

app.constant('timeRegexp', /(start|end):(\d{1,2})(:(\d{3}))?([ap]m)?/);

app.factory('CourseSearch', ['timeRegexp', function(timeRE){
	// score bonus for field matching
	var nameScore = 200,
		deptScore = 100,
		numberScore = 75,
		instructorScore = 50,
		creditsScore = 50,
		seatsScore = 50,
		commScore = 50,
		dowScore = 70,
		timeScore = 60;
	// score modifiers
	var beginningBonusMultiplier = 5,
		shortSubstringMaxScore = 1,
		negativeScore = -100000; // instant bad-match

	// "not a match" if less than this
	var cutoffScore = 50;

	function startsWith(str, substrs){
		return _.any(substrs, function(substr){
			return str.indexOf(substr) === 0;
		});
	}
	function stringAfterColon(str){
		return str.substr(str.indexOf(':') + 1);
	}

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

	var dowMatch = function(course, word){
		var day = {
			mon: 'Monday',
			monday: 'Monday',
			tue: 'Tuesday',
			tues: 'Tuesday',
			tuesday: 'Tuesday',
			wed: 'Wednesday',
			wednes: 'Wednesday',
			wednesday: 'Wednesday',
			thu: 'Thursday',
			thur: 'Thursday',
			thurs: 'Thursday',
			thursday: 'Thursday',
			fri: 'Friday',
			friday: 'Friday',
		}[word.toLowerCase()];

		if (day){
			var isMatch = _.any(course.sections, function(section){
				return _.any(section.section_times, function(section_time){
					return _.include(section_time.days_of_the_week, day);
				});
			});

			if (isMatch){
				return dowScore;
			}

			return negativeScore;
		}

		return 0;
	};

	var boolMatch = function(prefixes, word, score, cmp){
		if (startsWith(word, prefixes)){
			var bool = _.include(['1', 't', 'true', 'yes', 'enabled', 'only', 'on'],
								 stringAfterColon(word.toLowerCase()));
			return cmp(bool) ? score : negativeScore;
		}
		return 0;
	};

	var numberMatch = function(prefixes, word, score, cmp){
		if (startsWith(word, prefixes)){
			var num = parseInt(stringAfterColon(word.toLowerCase()), 10);
			if (!isNaN(num)){
				return cmp(num) ? score : negativeScore;
			}
		}
		return 0;
	};

	var timeMatch = function(course, word){
		var match = word.match(timeRE);
		if (match) {
			match.shift(); // entire match
			var isStart = match.shift() === 'start',
				hour = parseInt(match.shift(), 10),
				minuteOrAPM = match.shift(),
				minute = parseInt(minuteOrAPM || 0, 10);

			if (isNaN(minute)) {
				minute = 0;
			} else {
				minuteOrAPM = match.shift();
			}
			var isPM = (minuteOrAPM || 'am').toLowerCase() === 'pm';
			if (hour === 12) {
				hour -= 12;
			}
			if (isPM) {
				hour += 12;
			}
			var totalSeconds = hour * 3600 + minute * 60;
			var isMatch = _.any(course.sections, function(sections){
				return _.any(sections.section_times, function(section_time){
					return (
						(isStart && totalSeconds < section_time.start_time.totalSeconds) ||
						(!isStart && totalSeconds > section_time.end_time.totalSeconds)
					);
				});
			});
			if (isMatch){
				return timeScore;
			} else {
				return negativeScore;
			}
		}
		return 0;
	};

	return function(courses, query){
		var words = _.compact(query.toLowerCase().split(' '));
		return _(courses).chain().map(function(course){
			var courseName = course.name.toLowerCase();
			var deptCode = course.department.code.toLowerCase();
			var instructors = course.instructors().join(' ').toLowerCase();
			var seatsLeft = course.seatsLeft();
			var score = _.reduce(words, function(accum, word){
				var additiveScore = (
					matches(courseName, word, nameScore) +
					matches(deptCode, word, deptScore) +
					matches(String(course.number), word, numberScore) +
					matches(instructors, word, instructorScore) +
					numberMatch(['credit:', 'credits:'], word, creditsScore, function(n){
						return course.min_credits <= n && n <= course.max_credits;
					}) +
					numberMatch(['seats:', 'seats-left:', 'seatsleft:'], word, seatsScore, function(n){
						return seatsLeft < n;
					}) +
					boolMatch(['com:', 'comm:', 'communication:'], word, commScore, function(b){
						return course.is_comm_intense === b;
					}) +
					dowMatch(course, word) +
					timeMatch(course, word)
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
}]);

})(angular, app);

