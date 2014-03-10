'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("DepartmentCtrl", function(){
		var controller, semesterDeferred, departmentsDeferred, $location;
		beforeEach(inject(function($injector, $q, $controller, Semester, Department){
			$location = $injector.get('$location');
			semesterDeferred = $q.defer();
			departmentsDeferred = $q.defer();
			spyOn(Department, 'query').and.returnValue(departmentsDeferred.promise);
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
				semesterDeferred.resolve(new Semester({year: 2013, month: 1, id: 13}));
				$rootScope.$apply();
			}));

			it("should request for the departments for that semesmter", inject(function(Department){
				expect(Department.query).toHaveBeenCalledWith({semester_id: 13});
			}));

			describe("when the departments are resolved", function(){
				var departments;
				beforeEach(inject(function($rootScope, Department){
					departments = [new Department({code: 'CSCI'})];
					departmentsDeferred.resolve(departments);
					$rootScope.$apply();
				}));

				it("should set the results of the Department query to the scope", function(){
					expect(scope.departments).toEqual(departments);
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
});

})(document, angular, app);
