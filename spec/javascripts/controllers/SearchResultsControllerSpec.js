'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("SearchResultsCtrl", function(){
		var controller, $routeParams, semesterDeferred, CourseFetcher, CourseSearch, coursesDeferred;
		beforeEach(inject(function($controller, $q, $rootScope){
			coursesDeferred = $q.defer();
			CourseFetcher = jasmine.createSpy('CourseFetcher').andReturn(coursesDeferred.promise);
			CourseSearch = jasmine.createSpy('CourseSearch');

			semesterDeferred = $q.defer();
			$routeParams = {query: 'foo'};

			$rootScope.semester = semesterDeferred.promise;

			controller = $controller('SearchResultsCtrl', {
				$scope: scope,
				$routeParams: $routeParams,
				CourseFetcher: CourseFetcher,
				CourseSearch: CourseSearch
			});
		}));

		it("should courses on the scope", function(){
			expect(scope.courses).toEqual([]);
		});

		describe("when the semester promise is resolved", function(){
			beforeEach(inject(function(Semester, $rootScope){
				semesterDeferred.resolve(new Semester({id: 2, year: 2013, month: 1}));
				$rootScope.$apply();
			}));

			it("should tell the course fetcher to query for courses", function(){
				expect(CourseFetcher).toHaveBeenCalledWith({semester_id: 2});
			});

			describe("when the course fetcher is resolved", function(){
				var courses;
				beforeEach(inject(function($rootScope, Course){
					courses = [new Course(), new Course()];
					coursesDeferred.resolve(courses);
					CourseSearch.andReturn([courses[0]]);
					$rootScope.$apply();
				}));

				it("should use course search to filter courses", function(){
					expect(CourseSearch).toHaveBeenCalledWith(courses, 'foo');
				});

				it("should set the filtered courses on the scope", function(){
					expect(scope.courses).toEqual([courses[0]]);
				});
			});
		});
	});
});

})(document, angular, app);
