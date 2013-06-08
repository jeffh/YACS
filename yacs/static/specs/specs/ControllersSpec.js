'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("RootCtrl", function(){
		var controller, currentSemesterPromise, Selection, selectionDeferred;
		beforeEach(inject(function($q, $controller){
			selectionDeferred = $q.defer();
			currentSemesterPromise = $q.defer().promise;
			Selection = {
				current: selectionDeferred.promise
			};
			controller = $controller('RootCtrl', {
				$scope: scope,
				currentSemesterPromise: currentSemesterPromise,
				Selection: Selection
			});
		}));

		it("should set the current semester promise to the scope", function(){
			expect(scope.semester).toEqual(currentSemesterPromise);
		});


		describe("when then current selection is resolved", function(){
			var selection;
			beforeEach(inject(function($rootScope){
				selection = jasmine.createSpy('selection instance');
				selectionDeferred.resolve(selection);
				$rootScope.$apply();
			}));

			it("should set the current selection to the scope", function(){
				expect(scope.selection).toEqual(selection);
			});
		});
	});

	describe("FooterCtrl", function(){
		var controller;
		beforeEach(inject(function($controller){
			controller = $controller('FooterCtrl', {$scope: scope});
		}));

		it("should set the flavorText on the scope", function(){
			expect(scope.flavorText).toBeTruthy();
		});
	});

	describe("NavCtrl when the current semester is resolved", function(){
		var controller;
		beforeEach(inject(function($q, $rootScope, $controller, Semester){
			var semesterDeferred = $q.defer();
			semesterDeferred.resolve(new Semester({year: 2013, month: 1}));
			$rootScope.semester = semesterDeferred.promise;
			controller = $controller('NavCtrl', {
				$scope: scope,
			});
			$rootScope.$apply();
		}));

		it("should sets the items on the scope", function(){
			expect(_.pluck(scope.items, 'name')).toEqual(['Catalog', 'Selected']);
		});

		it("should set the selected item on the scope to Catalog", function(){
			expect(scope.selectedItem.name).toEqual('Catalog');
			expect(scope.items[0]).toEqual(scope.selectedItem);
		});

		describe("when 'selected' link is tapped", function(){
			var $location;
			beforeEach(inject(function($injector){
				$location = $injector.get('$location');
				$location.path('/foo/bar/');
				scope.click(scope.items[1]);
				scope.$apply();
			}));

			it("should update the location", function(){
				expect($location.path()).toEqual('/2013/1/selected/');
			});

			it("should update the selected item", function(){
				expect(scope.selectedItem).toEqual(scope.items[1]);
			});

			describe("tapping back to the 'catalog' link", function(){
				beforeEach(function(){
					scope.click(scope.items[0]);
					scope.$apply();
				});

				it("should revert back to the original location", function(){
					expect($location.path()).toEqual('/foo/bar/');
				});

				it("should update the selected item", function(){
					expect(scope.selectedItem).toEqual(scope.items[0]);
				});

				describe("tapping on the 'catalog' link one more time", function(){
					beforeEach(function(){
						scope.click(scope.items[0]);
						scope.$apply();
					});

					it("should revert back to the department list", function(){
						expect($location.path()).toEqual('/2013/1/');
					});

					it("should preserve the selected item", function(){
						expect(scope.selectedItem).toEqual(scope.items[0]);
					});
				});
			});
		});
	});

	describe("SearchCtrl", function(){
		var $route, $timeout, $location, controller, semesterDeferred, semester;
		beforeEach(inject(function($injector, $q, $controller, Semester, $rootScope){
			semester = new Semester({year: 2013, month: 1});
			semesterDeferred = $q.defer();
			semesterDeferred.resolve(semester);
			$rootScope.semester = semesterDeferred.promise;
			$route = {current: {params: {}}};

			$timeout = $injector.get('$timeout');
			$location = $injector.get('$location');
			controller = $controller('SearchCtrl', {
				$scope: scope,
				$route: $route
			});
		}));

		describe("when the semester promise is resolved with a query", function(){
			beforeEach(inject(function($rootScope){
				$location.path('/2013/1/search/foo/');
				$route.current.params.query = 'foo';
				semesterDeferred.resolve(semester);
				$rootScope.$apply();
			}));

			it("should fill the query in the scope", function(){
				expect(scope.query).toEqual('foo');
			});

			describe("when the user clears the query with a timeout", function(){
				beforeEach(function(){
					scope.query = '';
					scope.$apply();
					$timeout.flush();
				});

				it("should load the root location for the semester", function(){
					expect($location.path()).toEqual('/2013/1/');
				});
			});
		});

		describe("when the semester promise is resolved with no query", function(){
			beforeEach(inject(function($rootScope){
				$location.path('/prev/path/');
				semesterDeferred.resolve(semester);
				$rootScope.$apply();
			}));

			it("should set the query to an empty string", function(){
				expect(scope.query).toEqual('');
			});

			describe("when the user types into the query property with a timeout", function(){
				beforeEach(function(){
					scope.$apply(function(){ scope.query = 'ca'; });
					scope.$apply(function(){ scope.query = 'cake'; });
					$timeout.flush();
				});

				it("should change the location path", function(){
					expect($location.path()).toEqual('/2013/1/search/cake/');
				});

				describe("when the query is set back to an empty string", function(){
					beforeEach(function(){
						scope.query = '';
						scope.$apply();
						$timeout.flush();
					});

					it("should change the path back to what it was before the query", function(){
						expect($location.path()).toEqual('/prev/path/');
					});
				});
			});
		});
	});

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

	describe("DeptCtrl", function(){
		var controller, semesterDeferred, departmentsPromise, $location;
		beforeEach(inject(function($injector, $q, $controller, Semester, Department){
			$location = $injector.get('$location');
			semesterDeferred = $q.defer();
			departmentsPromise = $q.defer().promise;
			spyOn(Department, 'query').andReturn(departmentsPromise);
			controller = $controller('DeptCtrl', {
				$scope: scope,
				currentSemesterPromise: semesterDeferred.promise
			});
		}));

		it("should sets the departments to scope", function(){
			expect(scope.departments).toEqual([]);
		});

		describe("when the semester is resolved", function(){
			beforeEach(inject(function($rootScope, Semester){
				semesterDeferred.resolve(new Semester({year: 2013, month: 1}));
				$rootScope.$apply();
			}));

			it("should set the results of the Department query to the scope", function(){
				expect(scope.departments).toEqual(departmentsPromise);
			});

			describe("when clicking on a department", function(){
				beforeEach(inject(function(Department){
					scope.click(new Department({code: 'CSCI'}));
					scope.$apply();
				}));

				it("should change the location to the course list for that department", function(){
					expect($location.path()).toEqual('/2013/1/CSCI/');
				});
			});
		});
	});
});

})(document, angular, app);

