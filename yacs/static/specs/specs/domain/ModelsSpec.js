'use strict';

describe("Domain", function(){
	var apiClient, $rootScope, $q, conflictor;
	beforeEach(module(function($provide){
		conflictor = {
			courseConflictsAmongAllSections: jasmine.createSpy('conflictor.courseConflictsAmongAllSections')
		};
		$provide.value('conflictor', conflictor);

		apiClient = {get: jasmine.createSpy('apiClient.get')};
		$provide.value('apiClient', apiClient);
	}));

	beforeEach(inject(function($injector){
		$q = $injector.get('$q');
		$rootScope = $injector.get('$rootScope');
	}));

	describe("Models", function(){
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
					var $rootScope = $injector.get('$rootScope');
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
				beforeEach(inject(function(currentSemesterPromise, $rootScope){
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

		describe("Course", function(){
			var course;
			describe("seating", function(){
				beforeEach(inject(function(Course){
					course = new Course({
						sections: [
							{seats_taken: 2, seats_total: 1},
							{seats_taken: 2, seats_total: 10},
							{seats_taken: 4, seats_total: 10}
						]
					});
				}));

				it("should sum seats taken", function(){
					expect(course.seatsTaken()).toEqual(8);
				});

				it("should sum seats total", function(){
					expect(course.seatsTotal()).toEqual(21);
				});

				it("should compute seats left, but not overcount overflowing sections", function(){
					expect(course.seatsLeft()).toEqual(14);
				});

				it("should have a text display of seats left", function(){
					expect(course.seatsLeftText()).toEqual('14 seats');
				});

				it("should have a text display of seats left in the singular form", function(){
					course.sections = [{seats_taken:1, seats_total: 2}];
					expect(course.seatsLeftText()).toEqual('1 seat');
				});
			});

			describe("sectionsTypes", function(){
				beforeEach(inject(function(Course){
					course = new Course({
						sections: [
							{section_times: [{kind: 'LEC'}, {kind: 'LEC'}]},
							{section_times: [{kind: 'LEC'}, {kind: 'LAB'}]},
							{section_times: [{kind: 'STU'}]},
						]
					});
				}));

				it("should return unique types of section times", function(){
					expect(course.sectionTypes()).toEqual(['LEC', 'LAB', 'STU']);
				});
			});

			describe("creditsText", function(){
				describe("with equal min and max credits", function(){
					beforeEach(inject(function(Course){
						course = new Course({min_credits: 4, max_credits: 4});
					}));

					it("should display credits with no range", function(){
						expect(course.creditsText()).toEqual('4 credits');
					});

					it("should display credits in the singular form", function(){
						course.min_credits = course.max_credits = 1;
						expect(course.creditsText()).toEqual('1 credit');
					});
				});

				describe("with differing min and max credits", function(){
					beforeEach(inject(function(Course){
						course = new Course({min_credits: 1, max_credits: 4});
					}));

					it("should display credits with a range; always pluralized", function(){
						expect(course.creditsText()).toEqual('1 - 4 credits');
					});
				});
			});

			describe("computeProperties", function(){
			});

		});
	});
});

