'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("FooterCtrl", function(){
		var controller;
		beforeEach(inject(function($controller){
			controller = $controller('FooterCtrl', {$scope: scope});
		}));

		it("should set the flavorText on the scope", function(){
			expect(scope.flavorText).toBeTruthy();
		});
	});
});

})(document, angular, app);
