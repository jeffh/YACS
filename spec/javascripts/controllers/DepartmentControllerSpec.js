'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("DepartmentCtrl", function(){
		var controller, semesterDeferred, departmentsPromise, $location;
		beforeEach(inject(function($injector, $q, $controller, Semester, Department){
			$location = $injector.get('$location');
			semesterDeferred = $q.defer();
			departmentsPromise = $q.defer().promise;
			spyOn(Department, 'query').andReturn(departmentsPromise);
			controller = $controller('DepartmentCtrl', {
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
					expect($location.path()).toEqual('/semesters/2013/1/CSCI/');
				});
			});
		});
	});
});

})(document, angular, app);
