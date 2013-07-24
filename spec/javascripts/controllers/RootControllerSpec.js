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

		it("should sets the STATIC_URL to the scope", function(){
			expect(scope.STATIC_URL).toEqual('cakes/');
		});

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

});

})(document, angular, app);

