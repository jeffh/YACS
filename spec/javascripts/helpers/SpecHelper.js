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



