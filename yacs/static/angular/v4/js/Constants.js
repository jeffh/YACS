'use strict';

(function(angular, app, undefined){

app.constant('kSectionTimeTags', {
	LEC: {
		name: 'Lecture',
		title: 'This course has lecture, where the instructor teaches the course.',
		sort_order: 0
	},
	TES: {
		name: 'Testing',
		title: 'This course has a testing period outside normal lecture or recitation.',
		sort_order: 5
	},
	REC: {
		name: 'Recitation',
		title: 'This course has recitation, where problemsets and quizzes generally occur.',
		sort_order: 2
	},
	LAB: {
		name: 'Lab',
		title: 'This course has lab, where hands-on activities occur.',
		sort_order: 1
	},
	STU: {
		name: 'Studio',
		title: 'This course has studio',
		sort_order: 4
	}
});

app.constant('kCourseTags', {
	communicationIntensive: {
		name: 'Comm Intensive',
		title: 'This course counts as a communication intensive course.',
		classes: 'satisfies-requirement',
		sort_order: 10
	},
	passOrFail: {
		name: 'Pass/Fail',
		title: "This course's final grade is pass or fail instead of a GPA.",
		classes: 'pass_or_fail',
		sort_order: 11
	}
});

// unused, but for reference
var noteTypes = {
	crosslist: function(note){
		return {
			name: note.course,
			title: 'This course meets with ' + note.course,
			classes: 'crosslist',
			sort_order: 20
		};
	},
	prereq: function(note){
		return {
			name: note.course,
			title: 'This course requires ' + note.course + ' before you can take this course. Alternative you may talk to the instructors of the course.',
			classes: 'prereq',
			sort_order: 21
		};
	}
};


})(angular, app);

