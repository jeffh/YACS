'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("CatalogCtrl", function(){
		var controller, $location, $routeParams, CourseFetcher, coursesDeferred, semesterDeferred, selectionDeferred;
		beforeEach(inject(function($injector, $q, $controller, Selection){
			semesterDeferred = $q.defer();
			coursesDeferred = $q.defer();
			selectionDeferred = $q.defer();
			CourseFetcher = jasmine.createSpy('CourseFetcher').andReturn(coursesDeferred.promise);
			$location = $injector.get('$location');
			Selection.current = selectionDeferred.promise;
			$routeParams = {dept: 'CSCI'};
			controller = $controller('CatalogCtrl', {
				$scope: scope,
				$routeParams: $routeParams,
				CourseFetcher: CourseFetcher,
				currentSemesterPromise: semesterDeferred.promise,
				Selection: Selection
			});
		}));

		it("should set the courses on the scope", function(){
			expect(scope.courses).toEqual([]);
		});

		it("should sets the empty text on the scope", function(){
			expect(scope.emptyText).toBeTruthy();
		});

		describe("when the current semester is resolved", function(){
			beforeEach(inject(function($rootScope, Semester){
				semesterDeferred.resolve(new Semester({id: 4, year: 2013, month: 1}));
				$rootScope.$apply();
			}));

			it("should fetch the courses for the given department and semester", function(){
				expect(CourseFetcher).toHaveBeenCalledWith({
					semester_id: 4,
					department_code: 'CSCI'
				});
			});

			describe("when the course fetcher and selection resolved", function(){
				var courses, selection;
				beforeEach(inject(function($rootScope, Course, Selection){
					selection = new Selection();
					spyOn(selection, 'apply').andCallThrough();
					courses = [new Course()];
					coursesDeferred.resolve(courses);
					selectionDeferred.resolve(selection);
					$rootScope.$apply();
				}));

				it("should sets the courses on the scope", function(){
					expect(scope.courses).toEqual(courses);
				});

				it("should apply the selection to the courses", function(){
					expect(selection.apply).toHaveBeenCalledWith(courses);
				});
			});

			describe("when clicking on a course and all promises are resolved", function(){
				var selection, clickedCourse, courseUpdatedDeferred;
				beforeEach(inject(function($rootScope, $q, Selection, Course){
					coursesDeferred.resolve([new Course(), new Course()]);
					clickedCourse = new Course();
					courseUpdatedDeferred = $q.defer();
					selection = new Selection();
					spyOn(selection, 'updateCourse').andReturn(courseUpdatedDeferred.promise);
					selectionDeferred.resolve(selection);
					$rootScope.$apply();
					scope.clickCourse(clickedCourse);
					$rootScope.$apply();
				}));

				it("should update the selection", function(){
					expect(selection.updateCourse).toHaveBeenCalledWith(clickedCourse);
				});

				describe("when the selection has been updated successfully", function(){
					beforeEach(inject(function($rootScope){
						spyOn(selection, 'save');
						spyOn(selection, 'apply');
						courseUpdatedDeferred.resolve();
						$rootScope.$apply();
					}));

					it("should save the selection", function(){
						expect(selection.save).toHaveBeenCalled();
					});

					it("should apply the selection to the courses from the scope", function(){
						expect(selection.apply).toHaveBeenCalledWith(scope.courses);
					});
				});

				describe("when the selection has not been updated successfully", function(){
					beforeEach(inject(function($rootScope){
						spyOn(selection, 'apply');
						courseUpdatedDeferred.reject();
						$rootScope.$apply();
					}));

					it("should apply the selection to the courses to revert the user's selection", function(){
						expect(selection.apply).toHaveBeenCalledWith(scope.courses);
					});
				});
			});

			describe("when clicking on a section and selection is resolved", function(){
				var selection, clickedCourse, clickedSection, sectionUpdatedDeferred;
				beforeEach(inject(function($rootScope, $q, Selection, Course, Section){
					coursesDeferred.resolve([new Course(), new Course()]);
					clickedCourse = new Course();
					clickedSection = new Section();
					sectionUpdatedDeferred = $q.defer();
					selection = new Selection();
					spyOn(selection, 'updateSection').andReturn(sectionUpdatedDeferred.promise);
					selectionDeferred.resolve(selection);
					$rootScope.$apply();
					scope.clickSection(clickedCourse, clickedSection);
					$rootScope.$apply();
				}));

				it("should update the selection", function(){
					expect(selection.updateSection).toHaveBeenCalledWith(clickedCourse, clickedSection);
				});

				describe("when the selection has been updated successfully", function(){
					beforeEach(inject(function($rootScope){
						spyOn(selection, 'save');
						spyOn(selection, 'apply');
						sectionUpdatedDeferred.resolve();
						$rootScope.$apply();
					}));

					it("should save the selection", function(){
						expect(selection.save).toHaveBeenCalled();
					});

					it("should apply the selection to the courses from the scope", function(){
						expect(selection.apply).toHaveBeenCalledWith(scope.courses);
					});
				});

				describe("when the selection has not been updated successfully", function(){
					beforeEach(inject(function($rootScope){
						spyOn(selection, 'apply');
						sectionUpdatedDeferred.reject();
						$rootScope.$apply();
					}));

					it("should apply the selection to the courses to revert the user's selection", function(){
						expect(selection.apply).toHaveBeenCalledWith(scope.courses);
					});
				});
			});
		});
	});
});

})(document, angular, app);
