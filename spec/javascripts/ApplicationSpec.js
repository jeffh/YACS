'use strict';

describe("Application", function(){
	describe("module", function(){
		it("should be defined", function(){
			expect(angular.module('yacs')).not.toBe(null);
		});
	});

	describe("STATIC_URL", function(){
		var staticURL;
		beforeEach(function(){
			inject(function($injector){
				staticURL = $injector.get('STATIC_URL');
			})
		});

		it("should be defined", function(){
			expect(staticURL).toBeTruthy();
		});
	});
});

