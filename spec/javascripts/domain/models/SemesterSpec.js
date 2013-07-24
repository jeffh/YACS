'use strict';

describe("Domain", function(){
	describe("Models", function(){
		var apiClient, $rootScope, $q;
		beforeEach(module(function($provide){
			apiClient = {get: jasmine.createSpy('apiClient.get')};
			$provide.value('apiClient', apiClient);
		}));

		beforeEach(inject(function($injector){
			$q = $injector.get('$q');
			$rootScope = $injector.get('$rootScope');
		}));

		describe("currentSemesterPromise", function(){
			var resolvedValue, success, failure, semester;
			var latestDeferred, queryDeferred;
			beforeEach(inject(function(Semester, $q){
				semester = {}; // any uniq object
				success = failure = false;
				latestDeferred = $q.defer();
				queryDeferred = $q.defer();
				spyOn(Semester, 'query').andReturn(queryDeferred.promise);
				spyOn(Semester, 'latest').andReturn(latestDeferred.promise);
			}));

			describe("when no semester is set as the current", function(){
				beforeEach(inject(function($injector){
					var currentSemesterPromise = $injector.get('currentSemesterPromise');
					var route = {params: {}};
					latestDeferred.resolve(semester);
					currentSemesterPromise.then(function(v){ resolvedValue = v; });
					$rootScope.$broadcast('$routeChangeSuccess', route, null);
					$rootScope.$apply();
				}));

				it("should resolve as the latest semester", function(){
					expect(resolvedValue).toEqual(semester);
				});
			});

			describe("when a semester is set as the current", function(){
				beforeEach(inject(function(currentSemesterPromise){
					var route = {
						params: {
							year: "2013",
							month: "1"
						}
					};
					$rootScope.$broadcast('$routeChangeSuccess', route, null);
					$rootScope.$apply();

					currentSemesterPromise.then(function(v){ resolvedValue = v; });
					queryDeferred.resolve([semester]);
					$rootScope.$apply();
				}));

				it("should resolve as that semester", inject(function(Semester, currentSemesterPromise){
					expect(Semester.query).toHaveBeenCalledWith({year: '2013', month: '1'});
					expect(resolvedValue).toEqual(semester);
				}));
			});
		});

		describe("Semester", function(){
			describe("latest", function(){
				var semester;
				beforeEach(function(){
					var deferred = $q.defer();
					deferred.resolve([
						{id: 4},
						{id: 5},
						{id: 6}
					]);
					apiClient.get.andReturn(deferred.promise);
				});

				beforeEach(inject(function(Semester){
					Semester.latest().then(function(s){ semester = s; });
					$rootScope.$apply();
				}));

				it("should perform a query", function(){
					expect(apiClient.get).toHaveBeenCalledWith('/api/4/semesters/', {});
				});

				it("should return the first semester", inject(function(Semester){
					expect(semester).toEqual(new Semester({id: 4}));
				}));
			});
		});
	});
});
