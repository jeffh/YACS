'use strict';

describe("Computations", function(){
	describe("conflictor", function(){
		var conflictor, course;
		beforeEach(inject(function($injector){
			conflictor = $injector.get('conflictor');
		}));

		describe("sectionConflicts", function(){
			
		});

		describe("courseConflictNames", function(){
			beforeEach(inject(function(Course){
				course = new Course({
					sections: [
						{allConflicts: ['A', 'B']},
						{allConflicts: ['A', 'C']}
					]
				});
			}));

			it("should return all conflicts from all the sections", function(){
				expect(conflictor.courseConflictNames(course)).toEqual([
					['A', 'B'], ['A', 'C']
				]);
			});
		});

		describe("allSectionsAreConflicted", function(){
			var conflictedCourse, partiallyConflictedCourse, unconflictedCourse;
			beforeEach(inject(function(Course){
				unconflictedCourse = new Course({});
				partiallyConflictedCourse = new Course({
					sections: [
						{allConflicts: ['A', 'B']},
						{allConflicts: []}
					]
				});
				conflictedCourse = new Course({
					sections: [
						{allConflicts: ['A', 'B']}
					]
				});
			}));

			it("should be true for completely conflicted course", function(){
				expect(conflictor.isCourseConflicted(conflictedCourse)).toBeTruthy();
			});

			it("should be false for partially conflicted course", function(){
				expect(conflictor.isCourseConflicted(partiallyConflictedCourse)).toBeFalsy();
			});

			it("should be false for unconflicted course", function(){
				expect(conflictor.isCourseConflicted(unconflictedCourse)).toBeFalsy();
			});
		});

		describe("conflictsAmongAllSections", function(){
			describe("fully conflicted course", function(){
				beforeEach(inject(function(Course){
					course = new Course({
						sections: [
							{allConflicts: ['A', 'B']},
							{allConflicts: ['A', 'B', 'C']},
							{allConflicts: ['A', 'B', 'D']},
						]
					});
				}));

				it("should return all conflict names shared among all sections", function(){
					expect(conflictor.courseConflictsAmongAllSections(course)).toEqual(['A', 'B', 'C', 'D']);
				});
			});

			describe("non-conflicted course", function(){
				beforeEach(inject(function(Course){
					course = new Course({
						sections: [
							{allConflicts: ['A', 'B']},
							{allConflicts: []},
							{allConflicts: ['A', 'B', 'D']},
						]
					});
				}));

				it("should return an empty array", function(){
					expect(conflictor.courseConflictsAmongAllSections(course)).toEqual([]);
				});
			});
		});
	});
});
