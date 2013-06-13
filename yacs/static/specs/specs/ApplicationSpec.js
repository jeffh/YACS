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

		it("should not be null", function(){
			expect(staticURL).toBeTruthy();
		});
	});
	
	describe("urlProvider", function(){
		var getUrl;
		beforeEach(inject(function(urlProvider){
			getUrl = urlProvider;
		}));

		describe("when given arguments", function(){
			it("should return url with slashes between the args", function(){
				expect(getUrl('foo', 1)).toEqual('/foo/1/');
			});

			it("should encode the parameters", function(){
				expect(getUrl('http://google.com/')).toEqual('/' + encodeURIComponent('http://google.com/') + '/');
			});
		});

		describe("when given no arguments", function(){
			it("should return the root path", function(){
				expect(getUrl()).toEqual('/');
			});
		});
		
	});
});

