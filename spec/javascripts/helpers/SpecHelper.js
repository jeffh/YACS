'use strict';

angular.module('yacs')
.constant('STATIC_URL', '/STATIC/')
.constant('ICAL_URL', '/ICAL/');

beforeEach(module('yacs'));
beforeEach(function(){
    this.addMatchers({
        toBeAFunction: function(){
            return _.isFunction(this.actual);
        },
    });
});

beforeEach(module(function($provide){
	$provide.value('CSRF_TOKEN', 'csrf-token');
}));



