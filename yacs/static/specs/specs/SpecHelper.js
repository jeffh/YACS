'use strict';

beforeEach(module('yacs'));
beforeEach(function(){
    this.addMatchers({
        toBeAFunction: function(){
            return _.isFunction(this.actual);
        }
    });
});

