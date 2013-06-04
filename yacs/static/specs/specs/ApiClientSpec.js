'use strict';

describe("ApiClient", function(){
	var client, $httpBackend, $q;
	beforeEach(inject(function($injector){
		$httpBackend = $injector.get('$httpBackend');
		$q = $injector.get('$q');
		client = $injector.get('apiClient');
	}));
	
	afterEach(function() {
		$httpBackend.verifyNoOutstandingRequest();
	});
	
	describe("when getting a url with params", function(){
		var result;
		beforeEach(function(){
			var response = {success: true, result: [1, 2]};
			$httpBackend.whenGET('/api/4/?semester_id=1').respond(response);
			client.get('/api/4/', {semester_id: 1}).then(function(theResult){
				result = theResult;
			});
			$httpBackend.flush();
		});
		
		it("should perform an ajax request", function(){
			$httpBackend.expectGET('/api/4/?semester_id=1');
		});
		
		it("should resolve its promise with the result", function(){
			expect(result).toEqual([1, 2]);
		});
	});
	

	describe("when getting a url successfully", function(){
		var result;
		beforeEach(function(){
			var response = {success: true, result: [1, 2]};
			$httpBackend.whenGET('/api/4/').respond(response);
			client.get('/api/4/').then(function(theResult){
				result = theResult;
			});
			$httpBackend.flush();
		});
		
		it("should perform an ajax request", function(){
			$httpBackend.expectGET('/api/4/');
		});
		
		it("should resolve its promise with the result", function(){
			expect(result).toEqual([1, 2]);
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
			$httpBackend.whenGET('/api/4/').respond(response);
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
			$httpBackend.expectGET('/api/4/');
		});
	});
	
	describe("when getting a non-200 http response status code", function(){
		var err;
		beforeEach(function(){
			var response = {success: true, result: 2};
			$httpBackend.whenGET('/api/4/').respond(500, response);
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
			$httpBackend.expectGET('/api/4/');
		});
	});
});

