'use strict';

angular.module('yacs')
.constant('STATIC_URL', '/STATIC/')
.constant('ICAL_URL', '/ICAL/');

beforeEach(module('yacs'));
beforeEach(function(){
	jasmine.addMatchers({
		toBeAFunction: function(){
			return {
				compare: function(actual){
					return { pass: _.isFunction(actual) };
				}
			};
		},
	});
});

beforeEach(module(function($provide){
	$provide.value('CSRF_TOKEN', 'csrf-token');
}));

var allowStaticFetches = inject(function($httpBackend) {
	$httpBackend.whenGET(/.*STATIC.*/).respond(200);
});

var allowSemesterFetch = inject(function($httpBackend){
	$httpBackend.whenPOST('/api/4/semesters/').respond(200, {});
});
