'use strict';

describe("RootCtrl", function(){
	var scope, controller, location, currentSemesterDeferred, Selection,
		selectionDeferred, semestersDeferred;

	beforeEach(allowStaticFetches);

	beforeEach(inject(function($rootScope, $q, $controller, Semester){
		scope = $rootScope.$new();
		selectionDeferred = $q.defer();
		currentSemesterDeferred = $q.defer();
		semestersDeferred = $q.defer();
		Selection = {
			current: selectionDeferred.promise
		};
		Semester.query = function(){
			return semestersDeferred.promise;
		};
		location = {
			path: function(p) {
				location.received_path = p;
				return location;
			},
			search: function(s) {
				location.received_search = s;
				return location;
			}
		};
		controller = $controller('RootCtrl', {
			$scope: scope,
			$location: location,
			currentSemesterPromise: currentSemesterDeferred.promise,
			Selection: Selection,
			Semester: Semester
		});
	}));

	it("should set the STATIC_URL to the scope", function(){
		expect(scope.STATIC_URL).toEqual('/STATIC/');
	});

	describe("changing the current semester", function(){
		var newSemester, selection;
		beforeEach(inject(function($rootScope, Semester, Selection){
			selection = new Selection({1: [2, 3]}, []);
			selectionDeferred.resolve(selection);

			newSemester = new Semester({ id: 2, year: 2014, month: 1 });
			scope.changeToSemester(newSemester);

			$rootScope.$apply();
		}));

		it("should update the current semester on the scope", function(){
			expect(scope.semester).toEqual(newSemester);
		});

		it("should change the location to the new semester", function(){
			expect(location.received_path).toEqual('/semesters/2014/1/');
			expect(location.received_search).toEqual({});
		});

		it("should clear the user's selection", function(){
			expect(selection.numberOfCourses()).toEqual(0);
		});
	});

	describe("when the all the semesters promise is resolved", function(){
		var allSemesters;
		beforeEach(inject(function($rootScope, Semester){
			allSemesters = [new Semester({ id: 1 })];
			semestersDeferred.resolve(allSemesters);
			$rootScope.$apply();
		}));

		it("should set the semesters on the scope", function(){
			expect(scope.semesters).toEqual(allSemesters);
		});
	});

	describe("when the current semester promise is resolved", function(){
		var currentSemester;
		beforeEach(inject(function($rootScope, Semester){
			currentSemester = new Semester({id: 1});
			currentSemesterDeferred.resolve(currentSemester);
			$rootScope.$apply();
		}));

		it("should set the current semester to the scope", function(){
			expect(scope.semester).toEqual(currentSemester);
		});
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
