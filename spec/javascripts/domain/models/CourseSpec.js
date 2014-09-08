'use strict';

describe("Course", function(){
	var apiClient, $rootScope, $q, conflictor, tagger, course;

	beforeEach(module(function($provide){
		conflictor = {
			computeCourseConflicts: jasmine.createSpy('conflictor.computeCourseConflicts')
		};
		$provide.value('conflictor', conflictor);

		tagger = jasmine.createSpy('tagger');
		$provide.value('tagger', tagger);

		apiClient = {get: jasmine.createSpy('apiClient.get')};
		$provide.value('apiClient', apiClient);
	}));

	beforeEach(inject(function($injector){
		$q = $injector.get('$q');
		$rootScope = $injector.get('$rootScope');
	}));

	describe("seating", function(){
		beforeEach(inject(function(Course){
			course = new Course({
				sections: [
					{seats_taken: 2, seats_total: 1},
					{seats_taken: 2, seats_total: 10},
					{seats_taken: 4, seats_total: 10}
				]
			});
		}));

		it("should sum seats taken", function(){
			expect(course.seatsTaken()).toEqual(8);
		});

		it("should sum seats total", function(){
			expect(course.seatsTotal()).toEqual(21);
		});

		it("should compute seats left, but not overcount overflowing sections", function(){
			expect(course.seatsLeft()).toEqual(14);
		});

		it("should have a text display of seats left", function(){
			expect(course.seatsLeftText()).toEqual('14 seats');
		});

		it("should have a text display of seats left in the singular form", function(){
			course.sections = [{seats_taken:1, seats_total: 2}];
			expect(course.seatsLeftText()).toEqual('1 seat');
		});
	});

	describe("sectionsTypes", function(){
		beforeEach(inject(function(Course){
			course = new Course({
				sections: [
					{section_times: [{kind: 'LEC'}, {kind: 'LEC'}]},
					{section_times: [{kind: 'LEC'}, {kind: 'LAB'}]},
					{section_times: [{kind: 'STU'}]},
				]
			});
		}));

		it("should return unique types of section times", function(){
			expect(course.sectionTypes()).toEqual(['LEC', 'LAB', 'STU']);
		});
	});

	describe("creditsText", function(){
		describe("with equal min and max credits", function(){
			beforeEach(inject(function(Course){
				course = new Course({min_credits: 4, max_credits: 4});
			}));

			it("should display credits with no range", function(){
				expect(course.creditsText()).toEqual('4 credits');
			});

			it("should display credits in the singular form", function(){
				course.min_credits = course.max_credits = 1;
				expect(course.creditsText()).toEqual('1 credit');
			});
		});

		describe("with differing min and max credits", function(){
			beforeEach(inject(function(Course){
				course = new Course({min_credits: 1, max_credits: 4});
			}));

			it("should display credits with a range; always pluralized", function(){
				expect(course.creditsText()).toEqual('1 - 4 credits');
			});
		});
	});

	describe("computeProperties", function(){
		var tags;
		beforeEach(inject(function(Course, Section){
			tags = ['lol', 'tagz'];
			tagger.and.returnValue(tags);
			course = new Course({
				min_credits: 1,
				max_credits: 4,
				sections: _.map([
					{notes: "Foo"},
					{notes: "Bar"},
					{notes: "Bar"}
				], function(attrs){ return new Section(attrs); })
			});
			course.computeProperties();
		}));

		it("should compute conflicts", function(){
			expect(conflictor.computeCourseConflicts).toHaveBeenCalledWith(course);
		});

		it("should compute tags", function(){
			expect(tagger).toHaveBeenCalledWith(course);
			expect(course.tags).toEqual(tags);
		});

		it("should compute notes", function(){
			expect(course.notes).toEqual(["Foo", "Bar"]);
		});
	});
});
