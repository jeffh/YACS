'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(module(function($provide){
		$provide.constant('STATIC_URL', 'cakes/');
	}));
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("RootCtrl", function(){
		var controller, currentSemesterDeferred, Selection, selectionDeferred;
		beforeEach(inject(function($q, $controller){
			selectionDeferred = $q.defer();
			currentSemesterDeferred = $q.defer();
			Selection = {
				current: selectionDeferred.promise
			};
			controller = $controller('RootCtrl', {
				$scope: scope,
				currentSemesterPromise: currentSemesterDeferred.promise,
				Selection: Selection
			});
		}));

		it("should sets the STATIC_URL to the scope", function(){
			expect(scope.STATIC_URL).toEqual('cakes/');
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

});

})(document, angular, app);

