'use strict';

describe("Service", function(){
	describe("searchOptions", function(){
		var $rootScope, searchOptions;
		beforeEach(inject(function($injector){
			$rootScope = $injector.get('$rootScope');
			searchOptions = $injector.get('searchOptions');
		}));

		it("should initialize the default options", function(){
			expect(searchOptions.visible).toBeTruthy();
		});

		describe("when the route changes", function(){
			beforeEach(function(){
				searchOptions.visible = false;
				$rootScope.$broadcast('$routeChangeStart');
			});

			it("should reset the default options", function(){
				expect(searchOptions.visible).toBeTruthy();
			});
		});
	});
});

describe("SearchCtrl", function(){
	var $route, $timeout, $location, scope, controller, semester, searchOptions;

	beforeEach(allowStaticFetches);

	beforeEach(inject(function($rootScope, $injector, $controller, Semester, $rootScope){
		scope = $rootScope.$new();
		searchOptions = $injector.get('searchOptions');
		semester = new Semester({year: 2013, month: 1});
		$rootScope.semester = semester;
		$route = {current: {params: {}}};

		$timeout = $injector.get('$timeout');
		$location = $injector.get('$location');
		controller = $controller('SearchCtrl', {
			$scope: scope,
			$route: $route,
			searchOptions: searchOptions
		});
	}));

	it("should set the search options to the scope", function(){
		expect(scope.searchOptions).toBe(searchOptions);
	});

	describe("when the controller is loaded with a query", function(){
		beforeEach(inject(function($rootScope){
			$location.path('/2013/1/search/foo/');
			$route.current.params.query = 'foo';
			$rootScope.$apply();
		}));

		it("should fill the query in the scope", function(){
			expect(scope.query).toEqual('foo');
		});
	});

	describe("when the controller is loaded with no query", function(){
		beforeEach(inject(function($rootScope){
			$location.path('/prev/path/');
			$rootScope.$apply();
		}));

		it("should set the query to an empty string", function(){
			expect(scope.query).toEqual('');
		});

		describe("when the user types into the query property with a timeout", function(){
			beforeEach(function(){
				scope.$apply(function(){ scope.query = 'ca'; });
				scope.$apply(function(){ scope.query = 'cake'; });
				$timeout.flush();
			});

			it("should change the location path", function(){
				expect($location.path()).toEqual('/semesters/2013/1/search/cake/');
			});
		});
	});
});
