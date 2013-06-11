'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("SearchCtrl", function(){
		var $route, $timeout, $location, controller, semesterDeferred, semester;
		beforeEach(inject(function($injector, $q, $controller, Semester, $rootScope){
			semester = new Semester({year: 2013, month: 1});
			semesterDeferred = $q.defer();
			semesterDeferred.resolve(semester);
			$rootScope.semester = semesterDeferred.promise;
			$route = {current: {params: {}}};

			$timeout = $injector.get('$timeout');
			$location = $injector.get('$location');
			controller = $controller('SearchCtrl', {
				$scope: scope,
				$route: $route
			});
		}));

		describe("when the semester promise is resolved with a query", function(){
			beforeEach(inject(function($rootScope){
				$location.path('/2013/1/search/foo/');
				$route.current.params.query = 'foo';
				semesterDeferred.resolve(semester);
				$rootScope.$apply();
			}));

			it("should fill the query in the scope", function(){
				expect(scope.query).toEqual('foo');
			});
		});

		describe("when the semester promise is resolved with no query", function(){
			beforeEach(inject(function($rootScope){
				$location.path('/prev/path/');
				semesterDeferred.resolve(semester);
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
					expect($location.path()).toEqual('/2013/1/search/cake/');
				});
			});
		});
	});
});

})(document, angular, app);
