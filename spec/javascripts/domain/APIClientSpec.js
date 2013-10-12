'use strict';

describe("networkIndicator", function(){
	var $rootScope, networkIndicator;
	beforeEach(inject(function($injector){
		$rootScope = $injector.get('$rootScope');
		networkIndicator = $injector.get('networkIndicator');
	}));

	it("should start out hidden", function(){
		expect(networkIndicator.isVisible()).toBeFalsy();
	});

	describe("when the route changes", function(){
		beforeEach(function(){
			$rootScope.$broadcast('$routeChangeStart');
		});

		it("should show the indicator (by acquiring)", function(){
			expect(networkIndicator.isVisible()).toBeTruthy();
		});

		describe("when the route change finishes successfully", function(){
			beforeEach(function(){
				$rootScope.$broadcast('$routeChangeSuccess');
			});

			it("should be hidden", function(){
				expect(networkIndicator.isVisible()).toBeFalsy();
			});
		});

		describe("when the route fails to change", function(){
			beforeEach(function(){
				$rootScope.$broadcast('$routeChangeError');
			});

			it("should be hidden", function(){
				expect(networkIndicator.isVisible()).toBeFalsy();
			});
		});
	});

	describe("when acquired", function(){
		beforeEach(function(){
			networkIndicator.acquire();
		});

		it("should be visible", function(){
			expect(networkIndicator.isVisible()).toBeTruthy();
		});

		describe("when released", function(){
			beforeEach(function(){
				networkIndicator.release();
			});

			it("should be hidden", function(){
				expect(networkIndicator.isVisible()).toBeFalsy();
			});
		});
	});

	describe("when anyone still has the networkIndicator acquired", function(){
		beforeEach(function(){
			networkIndicator.acquire();
			networkIndicator.acquire();
			networkIndicator.acquire();
			networkIndicator.release();
			networkIndicator.acquire();
			networkIndicator.release();
			networkIndicator.release();
		});

		it("should still be visible", function(){
			expect(networkIndicator.isVisible()).toBeTruthy();
		});
	});
});


describe("ApiClient", function(){
	var client, $httpBackend, $q, networkIndicator;

	beforeEach(inject(function($injector){
		networkIndicator = $injector.get('networkIndicator');
		$httpBackend = $injector.get('$httpBackend');
		$q = $injector.get('$q');
		client = $injector.get('apiClient');
	}));

	afterEach(function() {
		$httpBackend.verifyNoOutstandingRequest();
	});

	describe("#get", function(){
		describe("when getting a url with params", function(){
			var result;
			beforeEach(function(){
				var response = {success: true, result: [1, 2]};
				$httpBackend.whenPOST('/api/4/', 'semester_id=1').respond(response);
				client.get('/api/4/', {semester_id: 1}).then(function(theResult){
					result = theResult;
				});
			});

			it("should perform an ajax post request with csrf_token", function(){
				$httpBackend.expectPOST('/api/4/', 'semester_id=1' , {'X-CSRFToken': 'csrf-token'});
			});

			it("should activate the network indicator", function(){
				expect(networkIndicator.isVisible()).toBeTruthy();
			});

			describe("when the request succeeds", function(){
				beforeEach(function(){
					$httpBackend.flush();
				});

				it("should resolve its promise with the result", function(){
					expect(result).toEqual([1, 2]);
				});
			});
		});

		describe("when getting a url successfully", function(){
			var result;
			beforeEach(function(){
				var response = {success: true, result: [1, 2]};
				$httpBackend.whenPOST('/api/4/').respond(response);
				client.get('/api/4/').then(function(theResult){
					result = theResult;
				});
				$httpBackend.flush();
			});

			it("should perform an ajax request", function(){
				$httpBackend.expectPOST('/api/4/');
			});

			it("should resolve its promise with the result", function(){
				expect(result).toEqual([1, 2]);
			});

			it("should release the network indicator", function(){
				expect(networkIndicator.isVisible()).not.toBeTruthy();
			});

			it("should cache the response", function(){
				var newResult;
				client.get('/api/4/').then(function(theResult){
					newResult = theResult;
				});
				$httpBackend.verifyNoOutstandingExpectation();
				expect(result).toEqual(newResult);
			});
		});

		describe("when getting a url with a success: false api response", function(){
			var err;
			beforeEach(function(){
				var response = {success: false};
				$httpBackend.whenPOST('/api/4/').respond(response);
				client.get('/api/4/').then(angular.noop, function(error){
					err = error;
				});
				$httpBackend.flush();
			});

			it("should reject its promise", function(){
				expect(err).toBeTruthy();
			});

			it("should not cache the response", function(){
				client.get('/api/4/');
				$httpBackend.expectPOST('/api/4/');
			});

			it("should release the network indicator", function(){
				expect(networkIndicator.isVisible()).not.toBeTruthy();
			});
		});

		describe("when getting a non-200 http response status code", function(){
			var err;
			beforeEach(function(){
				var response = {success: true, result: 2};
				$httpBackend.whenPOST('/api/4/').respond(500, response);
				client.get('/api/4/').then(angular.noop, function(error){
					err = error;
				});
			});

			it("should reject its promise", function(){
				$httpBackend.flush();
				expect(err).toBeTruthy();
			});

			it("should not cache the response", function(){
				client.get('/api/4/');
				$httpBackend.expectPOST('/api/4/');
			});
		});
	});
});

