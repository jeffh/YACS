'use strict';

describe("IndexCtrl", function(){
	var scope, controller, semesterDeferred, $location;
	beforeEach(allowStaticFetches);

	beforeEach(inject(function($rootScope, $injector, $controller, $q, $rootScope, Semester){
		scope = $rootScope.$new();
		$location = $injector.get('$location');
		semesterDeferred = $q.defer();
		controller = $controller('IndexCtrl', {
			$scope: scope,
			currentSemesterPromise: semesterDeferred.promise
		});
	}));

	describe("when the current semester is resolved", function(){
		beforeEach(inject(function(Semester, $rootScope){
			semesterDeferred.resolve(new Semester({id: 1, year: 2013, month: 1}));
			$rootScope.$apply();
		}));

		it("should change the location to the department list", function(){
			expect($location.path()).toEqual('/semesters/2013/1/');
		});
	});
});
