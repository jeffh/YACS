'use strict';

describe('Utils', function(){
	var Utils;
	beforeEach(inject(['Utils', function(theUtils){
		Utils = theUtils;
	}]));

	describe("queryString", function(){
		it("should return a querystring from an object", function(){
			var query = Utils.queryString({foo: 1, bar: 'baz'});
			expect(query).toEqual('foo=1&bar=baz');
		});

		describe("when given a parameter with an array", function(){
			it("should comma separate the parameter values", function(){
				var query = Utils.queryString({foo: [1, 2]});
				expect(query).toEqual('foo=1,2');
			});
		});
	});

	describe("URL", function(){
		var fn;
		beforeEach(function(){
			fn = Utils.URL('/foo/bar/');
		});

		it("should generate a function", function(){
			expect(fn).toBeAFunction();
		});

		describe("the generated function", function(){
			describe("when given no arguments", function(){
				it("should return the provided url", function(){
					expect(fn()).toEqual('/foo/bar/');
				});
			});

			describe("when an id is given", function(){
				it("should generate an url with the id appended to it", function(){
					expect(fn(1)).toEqual('/foo/bar/1');
				});
			});
		});
	});

	describe("product", function(){
		it("produces all possible permutations", function(){
			var domains = [
				[1, 2],
				[3, 4, 5]
			];
			var possibilities = Utils.product(domains).sort();
			expect(possibilities).toEqual([
				[1, 3],
				[1, 4],
				[1, 5],
				[2, 3],
				[2, 4],
				[2, 5]
			].sort());
		});

		it("should can be arbitrary number of variables", function(){
			var domains = [
				[1, 2],
				[3, 4],
				[5, 6]
			];
			var possibilities = Utils.product(domains).sort();
			expect(possibilities).toEqual([
				[1, 3, 5],
				[1, 3, 6],
				[1, 4, 5],
				[1, 4, 6],
				[2, 3, 5],
				[2, 3, 6],
				[2, 4, 5],
				[2, 4, 6],
			].sort());
		});
	});

	describe('pluralize', function(){
		describe("when the number is 1", function(){
			it("should not pluralize the string", function(){
				expect(Utils.pluralize('foo', 1)).toEqual('foo');
			});
		});

		describe("when the number is not 1", function(){
			it("should append an 's'", function(){
				expect(Utils.pluralize('cake', 2)).toEqual('cakes');
			});
		});
	});

	describe("hashById", function(){
		describe("when the property argument is provided", function(){
			var obj1, obj2;
			beforeEach(function(){
				obj1 = {cake: 1};
				obj2 = {cake: 2};
			});

			it("should sort by the given property id", function(){
				expect(Utils.hashById([obj1, obj2], 'cake')).toEqual({1: obj1, 2: obj2});
			});
		});

		describe("when the property argument is not provided", function(){
			var obj1, obj2;
			beforeEach(function(){
				obj1 = {id: 1};
				obj2 = {id: 2};
			});

			it("should default to 'id'", function(){
				expect(Utils.hashById([obj1, obj2])).toEqual({1: obj1, 2: obj2});
			});
		});
	});
});
