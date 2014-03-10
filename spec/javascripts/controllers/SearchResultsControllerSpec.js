'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("SearchResultsCtrl", function(){
		var controller, $routeParams,
			semesterDeferred, CourseFetcher,
			CourseSearch, coursesDeferred,
			selectionDeferred;
		beforeEach(inject(function($controller, $q, $rootScope, Selection){
			selectionDeferred = $q.defer();
			coursesDeferred = $q.defer();
			Selection.current = selectionDeferred.promise;
			CourseFetcher = jasmine.createSpy('CourseFetcher').and.returnValue(coursesDeferred.promise);
			CourseSearch = jasmine.createSpy('CourseSearch');

			semesterDeferred = $q.defer();
			$routeParams = {query: 'foo'};

			$rootScope.semester = semesterDeferred.promise;

			controller = $controller('SearchResultsCtrl', {
				$scope: scope,
				$routeParams: $routeParams,
				CourseFetcher: CourseFetcher,
				CourseSearch: CourseSearch,
				Selection: Selection
			});
		}));

		it("should courses on the scope", function(){
			expect(scope.courses).toEqual([]);
		});

		describe("when the semester and selection promise is resolved", function(){
			var selection;
			beforeEach(inject(function(Semester, $rootScope, Selection){
				selection = new Selection();
				semesterDeferred.resolve(new Semester({id: 2, year: 2013, month: 1}));
				selectionDeferred.resolve(selection);
				$rootScope.$apply();
			}));

			it("should tell the course fetcher to query for courses", function(){
				expect(CourseFetcher).toHaveBeenCalledWith({semester_id: 2});
			});

			describe("when the course fetcher is resolved", function(){
				var courses;
				beforeEach(inject(function($rootScope, Course){
					spyOn(selection, 'apply').and.callThrough();
					courses = [new Course(), new Course()];
					coursesDeferred.resolve(courses);
					CourseSearch.and.returnValue([courses[0]]);
					$rootScope.$apply();
				}));

				it("should apply the selection to the courses", function(){
					expect(selection.apply).toHaveBeenCalledWith([courses[0]]);
				});

				it("should use course search to filter courses", function(){
					expect(CourseSearch).toHaveBeenCalledWith(courses, 'foo');
				});

				it("should set the filtered courses on the scope", function(){
					expect(scope.courses).toEqual([courses[0]]);
				});
			});

			describe("when clicking on a course and all promises are resolved", function(){
				var clickedCourse, courseUpdatedDeferred;
				beforeEach(inject(function($rootScope, $q, Selection, Course){
					coursesDeferred.resolve([new Course(), new Course()]);
					clickedCourse = new Course();
					courseUpdatedDeferred = $q.defer();
					spyOn(selection, 'updateCourse').and.returnValue(courseUpdatedDeferred.promise);
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
				var clickedCourse, clickedSection, sectionUpdatedDeferred;
				beforeEach(inject(function($rootScope, $q, Selection, Course, Section){
					coursesDeferred.resolve([new Course(), new Course()]);
					clickedCourse = new Course();
					clickedSection = new Section();
					sectionUpdatedDeferred = $q.defer();
					spyOn(selection, 'updateSection').and.returnValue(sectionUpdatedDeferred.promise);
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
