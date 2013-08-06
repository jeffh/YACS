'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("IndexCtrl", function(){
		var controller, semesterDeferred, $location;
		beforeEach(inject(function($injector, $controller, $q, $rootScope, Semester){
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
});

})(document, angular, app);
