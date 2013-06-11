'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("SelectionCtrl", function(){
		var controller, semesterDeferred, CourseFetcher, selectionDeferred, coursesDeferred;
		beforeEach(inject(function($controller, $q, Selection){
			coursesDeferred = $q.defer();
			semesterDeferred = $q.defer();
			selectionDeferred = $q.defer();
			CourseFetcher = jasmine.createSpy('CourseFetcher').andReturn(coursesDeferred.promise);
			Selection.current = selectionDeferred.promise;
			controller = $controller('SelectionCtrl', {
				$scope: scope,
				currentSemesterPromise: semesterDeferred.promise,
				CourseFetcher: CourseFetcher,
				Selection: Selection
			});
		}));

		it("should set the courses on the scope", function(){
			expect(scope.courses).toEqual([]);
		});

		describe("when the current semester and selection are resolved", function(){
			var selection;
			beforeEach(inject(function($rootScope, Semester, Selection){
				selection = new Selection({2: [3], 4: [5]});
				spyOn(selection, 'apply');
				semesterDeferred.resolve(new Semester({id: 12}));
				selectionDeferred.resolve(selection);
				$rootScope.$apply();
			}));

			it("should query for its courses in its selection", function(){
				expect(CourseFetcher).toHaveBeenCalledWith({
					semester_id: 12,
					id: ['2', '4']
				});
			});

			describe("when the courses query is resolved", function(){
				var courses;
				beforeEach(inject(function($rootScope, Course){
					courses = [new Course()];
					coursesDeferred.resolve(courses);
					$rootScope.$apply();
				}));

				it("should updates the courses on the scope", function(){
					expect(scope.courses).toEqual(courses);
				});

				it("should apply the current selection to the courses", function(){
					expect(selection.apply).toHaveBeenCalledWith(courses);
				});

				it("should disable the search bar", function(){
					expect(scope.hideSearchBar).toBeTruthy();
				});

				describe("when clicking a course", function(){
					var clickedCourse, updateCourseDeferred;
					beforeEach(inject(function($rootScope, $q, Course){
						updateCourseDeferred = $q.defer();
						spyOn(selection, 'updateCourse').andReturn(updateCourseDeferred.promise);
						spyOn(selection, 'save');
						clickedCourse = new Course();
						scope.click_course(clickedCourse);
					}));

					it("should call updateCourse for the selection", function(){
						expect(selection.updateCourse).toHaveBeenCalledWith(clickedCourse);
					});

					describe("when the selection has been updated successfully", function(){
						beforeEach(inject(function($rootScope){
							updateCourseDeferred.resolve();
							$rootScope.$apply();
						}));

						it("should save the selection", function(){
							expect(selection.save).toHaveBeenCalled();
						});

						it("should apply the selection to the scope's courses", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});

					describe("when the selection has failed to update", function(){
						beforeEach(inject(function($rootScope){
							updateCourseDeferred.reject();
							$rootScope.$apply();
						}));

						it("should apply the selection to revert the user's change", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});
				});

				describe("when clicking a section", function(){
					var clickedCourse, clickedSection, updateSectionDeferred;
					beforeEach(inject(function($rootScope, $q, Course, Section){
						updateSectionDeferred = $q.defer();
						spyOn(selection, 'updateSection').andReturn(updateSectionDeferred.promise);
						spyOn(selection, 'save');
						clickedCourse = new Course();
						clickedSection = new Section();
						scope.click_section(clickedCourse, clickedSection);
					}));

					it("should call updateSection", function(){
						expect(selection.updateSection).toHaveBeenCalledWith(clickedCourse, clickedSection);
					});

					describe("when the selection has been updated successfully", function(){
						beforeEach(inject(function($rootScope){
							updateSectionDeferred.resolve();
							$rootScope.$apply();
						}));

						it("should save the selection", function(){
							expect(selection.save).toHaveBeenCalled();
						});

						it("should apply the selection to the scope's courses", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});

					describe("when the selection has failed to update", function(){
						beforeEach(inject(function($rootScope){
							updateSectionDeferred.reject();
							$rootScope.$apply();
						}));

						it("should apply the selection to revert the user's change", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});
				});
			});
		});
	});
});

})(document, angular, app);
