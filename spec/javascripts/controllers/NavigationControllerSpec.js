'use strict';

(function(document, angular, app, undefined){

describe("Controllers", function(){
	var scope;
	beforeEach(inject(function($rootScope){
		scope = $rootScope.$new();
	}));

	describe("NavCtrl", function(){
		var catalogIndex = 0,
			selectedIndex = 1;

		describe("when the current semester is resolved on the selected controller", function(){
			var controller, catalogItem, selectedItem;
			beforeEach(inject(function($location, $q, $rootScope, $controller, Semester){
				$location.path('/semesters/2013/1/selected/');
				var semesterDeferred = $q.defer();
				semesterDeferred.resolve(new Semester({year: 2013, month: 1}));
				$rootScope.semester = semesterDeferred.promise;
				controller = $controller('NavCtrl', {
					$scope: scope
				});
				$rootScope.$apply();
			}));

			it("should set the selected item to the selected link", function(){
				expect(scope.selectedItem).toEqual(scope.items[selectedIndex]);
			});
		});

		describe("when the current semester is resolved on the departments controller", function(){
			var controller, catalogItem, selectedItem;
			beforeEach(inject(function($q, $rootScope, $controller, Semester){
				var semesterDeferred = $q.defer();
				semesterDeferred.resolve(new Semester({year: 2013, month: 1}));
				$rootScope.semester = semesterDeferred.promise;
				controller = $controller('NavCtrl', {
					$scope: scope,
				});
				$rootScope.$apply();

				catalogItem = scope.items[catalogIndex];
				selectedItem = scope.items[selectedIndex];
			}));

			it("should sets the items on the scope", function(){
				expect(_.pluck(scope.items, 'name')).toEqual(['Catalog', 'Selected']);
			});

			it("should set the selected item on the scope to Catalog", function(){
				expect(scope.selectedItem.name).toEqual('Catalog');
				expect(scope.items[0]).toEqual(scope.selectedItem);
			});

			describe("when the selection is updated", function(){
				beforeEach(inject(function($rootScope, Selection){
					scope.selection = new Selection({1: [2, 3]});
					scope.$apply();
				}));

				it("should show the number of selected courses on the selected link", function(){
					expect(selectedItem.name).toEqual('Selected (1)');
				});
			});

			describe("when 'selected' link is tapped", function(){
				var $location;
				beforeEach(inject(function($injector){
					$location = $injector.get('$location');
					$location.path('/2013/1/CSCI/');
					scope.click(selectedItem);
					scope.$apply();
				}));

				it("should update the location", function(){
					expect($location.path()).toEqual('/semesters/2013/1/selected/');
				});

				it("should update the selected item", function(){
					expect(scope.selectedItem).toEqual(selectedItem);
				});

				var catalogCtrls = [
					{name: 'department', klass: 'DepartmentCtrl', url: '/semesters/2013/1/'},
					{name: 'catalog', klass: 'CatalogCtrl', url: '/semesters/2013/1/CSCI/'},
					{name: 'search results', klass: 'SearchResultsCtrl', url: '/semesters/2013/1/search/CSCI/'},
				];
				_(catalogCtrls).each(function(ctrl){
					describe("when going back to " + ctrl.name + " controller", function(){
						beforeEach(inject(function($rootScope){
							var route = {controller: ctrl.klass};
							$location.path(ctrl.url);
							$rootScope.$broadcast('$routeChangeSuccess', route);
						}));

						it("should select the catalog link", function(){
							expect(scope.selectedItem).toEqual(catalogItem);
						});
					});
				});

				describe("when going back to selection controller", function(){
					beforeEach(inject(function($rootScope){
						var route = {controller: 'SelectionCtrl'};
						scope.$broadcast('$routeChangeSuccess', route);
						scope.$apply();
					}));

					it("should select the selected link", function(){
						expect(scope.selectedItem).toEqual(selectedItem);
					});
				});

				describe("tapping on the 'catalog' link", function(){
					beforeEach(function(){
						scope.click(catalogItem);
						scope.$apply();
					});

					it("should revert back to the department list", function(){
						expect($location.path()).toEqual('/semesters/2013/1/');
					});

					it("should preserve the selected item", function(){
						expect(scope.selectedItem).toEqual(catalogItem);
					});
				});
			});
		});
	});
});

})(document, angular, app);
