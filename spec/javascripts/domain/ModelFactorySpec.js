'use strict';

describe("ModelFactory", function(){
	var apiClient, MyModel, deferred, $q, $rootScope;

	beforeEach(module(function($provide){
		apiClient = {get: jasmine.createSpy('apiClient.get')};
		$provide.value('apiClient', apiClient);
		console.log('module');
	}));

	beforeEach(allowStaticFetches);

	beforeEach(inject(function(ModelFactory, _$q_, _$rootScope_){
		$q = _$q_;
		$rootScope = _$rootScope_;
		MyModel = ModelFactory('MyModel', {
			defaults: {
				rofl: 'coptor',
				roller: 'coaster'
			},
			query: '/foo',
			get: function(id){ return '/foo/' + id; }
		});

		deferred = $q.defer();
		apiClient.get.and.returnValue(deferred.promise);
	}));

	describe("constructor", function(){
		var instance;

		describe("with no arguments", function(){
			beforeEach(function(){
				instance = new MyModel();
			});

			it("should set default attributes", function(){
				expect(instance.rofl).toEqual('coptor');
				expect(instance.roller).toEqual('coaster');
			});

			it("can be converted to a normal object", function(){
				expect(instance.toObject()).toEqual({rofl: 'coptor', roller: 'coaster'});
			});
		});

		describe("with an object argument", function(){
			beforeEach(function(){
				instance = new MyModel({foo: 'bar', id: 1, roller: 'blade'});
			});

			it("should assign attributes to itself", function(){
				expect(instance.foo).toEqual('bar');
				expect(instance.id).toEqual(1);
			});

			it("should overwrite default attributes with custom ones", function(){
				expect(instance.roller).toEqual('blade');
			});

			it("can be converted to a normal object", function(){
				expect(instance.toObject()).toEqual({rofl: 'coptor', roller: 'blade', foo: 'bar', id: 1});
			});
		});
	});
	

	describe("#query", function(){
		var collection;
		beforeEach(function(){
			deferred.resolve([{id: 1}, {id: 2}]);
		});

		describe("with filters", function(){
			beforeEach(function(){
				MyModel.query({dept_id: 2}).then(function(result){
					collection = result;
				});
			});
			
			it("should request the query url", function(){
				expect(apiClient.get).toHaveBeenCalledWith('/foo', {dept_id: 2});
			});

			it("should return a collection of the models", function(){
				$rootScope.$apply();
				expect(collection).toEqual([
					new MyModel({id: 1}),
					new MyModel({id: 2})
				]);
			});
		});

		describe("with no filters", function(){
			beforeEach(function(){
				MyModel.query().then(function(result){
					collection = result;
				});
			});
			
			it("should request the query url", function(){
				expect(apiClient.get).toHaveBeenCalledWith('/foo', {});
			});
		});
	});
	

	describe("#get", function(){
		var model;
		beforeEach(function(){
			deferred.resolve({id: 1, attr: 'value'});
			MyModel.get(2).then(function(instance){
				model = instance;
			});
		});

		it("should request the get url", function(){
			expect(apiClient.get).toHaveBeenCalledWith('/foo/2');
		});

		it("should return a single instance of the model", function(){
			$rootScope.$apply();
			expect(model).toEqual(new MyModel({id: 1, attr: 'value'}));
		});
	});


	describe("equals", function(){
		it("should be equal by ids", function(){
			expect(new MyModel({id: 1}).equals(new MyModel({id: 1, foo: 'bar'}))).toBe(true);
		});
	});
	
	describe("refresh", function(){
		var model, self;
		beforeEach(function(){
			deferred.resolve({id: 2, attr: 'value'});
			model = new MyModel({id: 2});
			model.refresh().then(function(instance){
				self = instance;
			});
			$rootScope.$apply();
		});

		it("should make an api request", function(){
			expect(apiClient.get).toHaveBeenCalledWith('/foo/2');
		});

		it("should resolve with the same instance", function(){
			expect(model).toBe(self);
		});

		it("should update the attributes of the instance", function(){
			expect(model.attr).toEqual('value');
		});
		
	});
});
