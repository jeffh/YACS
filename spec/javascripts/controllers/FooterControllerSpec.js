'use strict';

describe("FooterCtrl", function(){
	var scope, controller;

	beforeEach(inject(function($rootScope, $controller){
		scope = $rootScope.$new();
		controller = $controller('FooterCtrl', {$scope: scope});
	}));

	it("should set the flavorText on the scope", function(){
		expect(scope.flavorText).toBeTruthy();
	});
});
