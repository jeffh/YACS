'use strict';

describe("Domain", function(){
	describe("scheduleValidator", function(){
		var scheduleValidator, Semester, Conflict, Section;
		var semesterDeferred, conflictDeferred, sectionDeferred;
		beforeEach(module(function($provide){
			$provide.factory('currentSemesterPromise', function($q){
				semesterDeferred = $q.defer();
				return semesterDeferred.promise;
			});
		}));

		beforeEach(inject(function($injector, $rootScope, $q, currentSemesterPromise){
			scheduleValidator = $injector.get('scheduleValidator');
			Conflict = $injector.get('Conflict');
			Section = $injector.get('Section');

			conflictDeferred = $q.defer();
			sectionDeferred = $q.defer();
			spyOn(Conflict, 'query').andReturn(conflictDeferred.promise);
			spyOn(Section, 'query').andReturn(sectionDeferred.promise);
		}));

		describe("when the semester promise is resolved", function(){
			beforeEach(inject(function(Semester, $rootScope){
				semesterDeferred.resolve(new Semester({id: 42}));
				$rootScope.$apply();
			}));

			it("should query for conflicts", function(){
				expect(Conflict.query).toHaveBeenCalledWith({semester_id: 42});
			});

			it("should query for sections", function(){
				expect(Section.query).toHaveBeenCalledWith({semester_id: 42});
			});

			describe("when courses and conflicts are resolved", function(){
				var validator, rootScope;
				function classify(klass){
					return function(attrs){ return new klass(attrs); };
				}
				function grab(promise){
					var result;
					promise.then(function(v){ result = v; });
					rootScope.$apply();
					return result;
				}


				beforeEach(inject(function($rootScope, scheduleValidator, Conflict, Section){
					conflictDeferred.resolve(_([
						{id: 1, conflicts: [2, 3]},
						{id: 2, conflicts: [1]},
						{id: 3, conflicts: [1]},
						{id: 4, conflicts: []},
					]).map(classify(Conflict)));
					rootScope = $rootScope;
					validator = scheduleValidator;
				}));

				describe("conflictsWith", function(){
					beforeEach(function(){
						sectionDeferred.resolve(_([
							{id: 1}, {id: 2}, {id: 3}, {id: 4},
						]).map(classify(Section)));
						rootScope.$apply();
					});

					it("should check multiple courses", function(){
						expect(grab(validator.conflictsWith({1: [4], 2: [1]}, 2))).toBeTruthy();
					});

					it("should return true when sectionId conflicts with schedule", function(){
						expect(grab(validator.conflictsWith({1: [1, 4]}, 2))).toBeTruthy();
					});

					it("should return false when sectionId does not conflicts with schedule", function(){
						expect(grab(validator.conflictsWith({1: [2, 4]}, 2))).toBeFalsy();
						expect(grab(validator.conflictsWith({1: [2, 3]}, 2))).toBeFalsy();
					});
				});

				describe("isValid / computeSchedules", function(){
					var sections;
					beforeEach(function(){
						sections = _([
							{id: 1, section_times:[
								{
									days_of_the_week: ['Monday'],
									start: "10:00:00",
									end: "11:50:00"
								},
								{
									days_of_the_week: ['Thursday'],
									start: "10:00:00",
									end: "11:50:00"
								}
							]},
							{id: 2, section_times:[{
								days_of_the_week: ['Monday'],
								start: "10:50:00",
								end: "11:50:00"
							}]},
							{id: 3, section_times:[{
								days_of_the_week: ['Monday'],
								start: "13:00:00",
								end: "14:50:00"
							}]},
							{id: 4, section_times:[{
								days_of_the_week: ['Tuesday'],
								start: "10:00:00",
								end: "11:50:00"
							}]},
							{id: 5, section_times:[
								{
									days_of_the_week: ['Thursday'],
									start: "10:00:00",
									end: "12:50:00"
								},
								{
									days_of_the_week: ['Friday'],
									start: "10:00:00",
									end: "12:50:00"
								}
							]},
							{id: 6, section_times:[
								{
									days_of_the_week: ['Friday'],
									start: "10:00:00",
									end: "12:50:00"
								},
								{
									days_of_the_week: ['Monday'],
									start: "10:00:00",
									end: "12:50:00"
								}
							]}
						]).map(classify(Section));
						sectionDeferred.resolve(sections);
						rootScope.$apply();
					});

					it("should return false for overlapping times", function(){
						expect(grab(validator.isValid({1: [1], 2: [2]}))).toBeFalsy();
						expect(grab(validator.computeSchedules({1: [1], 2: [2]}))).toEqual([]);
					});

					it("should return false for identical times", function(){
						expect(grab(validator.isValid({1: [1], 2: [1]}))).toBeFalsy();
					});

					it("should return true for non-overlapping times on the same day", function(){
						expect(grab(validator.isValid({1: [1], 2: [3]}))).toBeTruthy();
						expect(grab(validator.computeSchedules({1: [1], 2: [3]}))).toEqual([{1: sections[0], 2: sections[2]}]);
					});

					it("should return true for overlapping times, but on different days", function(){
						expect(grab(validator.isValid({1: [1], 2: [4]}))).toBeTruthy();
						expect(grab(validator.computeSchedules({1: [1], 2: [4]}))).toEqual([{1: sections[0], 2: sections[3]}]);
					});

					it("can compute all schedules", function(){
						expect(grab(validator.computeSchedules({1: [1, 3, 4]}))).toEqual([
							{1: sections[0]},
							{1: sections[2]},
							{1: sections[3]}
						]);
					});

					it("can compute a restricted set of schedules", function(){
						expect(grab(validator.computeSchedules({1: [1, 3, 4]}, 2))).toEqual([
							{1: sections[0]},
							{1: sections[2]}
						]);
					});


					it("should return true if at least one section is valid for all courses", function(){
						var schedule = {
							1: [1, 3],
							2: [2]
						};
						expect(grab(validator.isValid(schedule))).toBeTruthy();
						expect(grab(validator.computeSchedules(schedule))).toEqual([{1: sections[2], 2: sections[1]}]);
					});

					it("should return false for cyclic conflicts", function(){
						var schedule = {
							1: [1],
							2: [5],
							3: [6]
						};
						expect(grab(validator.isValid(schedule))).toBeFalsy();
					});
				});
			});
		});
	});
});
