'use strict';

describe("Domain", function(){
	describe("Models", function(){
		var apiClient, $rootScope, $q, conflictor, tagger;
		beforeEach(module(function($provide){
			conflictor = {
				computeCourseConflicts: jasmine.createSpy('conflictor.computeCourseConflicts')
			};
			$provide.value('conflictor', conflictor);

			tagger = jasmine.createSpy('tagger');
			$provide.value('tagger', tagger);

			apiClient = {get: jasmine.createSpy('apiClient.get')};
			$provide.value('apiClient', apiClient);
		}));

		beforeEach(inject(function($injector){
			$q = $injector.get('$q');
			$rootScope = $injector.get('$rootScope');
		}));

		describe("Department", function(){
		});
	});
});

