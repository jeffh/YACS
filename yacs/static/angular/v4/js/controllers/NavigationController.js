'use strict';

(function(angular, app, undefined){

app.controller('NavCtrl', ['$scope', '$location', 'urlProvider',
			   function($scope, $location, urlProvider){
	$scope.semester.then(function(semester){
		var catalogItem = {
			name: 'Catalog',
			path: urlProvider.semester(semester.year, semester.month),
			controllers: ['CatalogCtrl', 'DeptCtrl', 'SearchResultsCtrl']
		};
		var selectedItem = {
			name: 'Selected',
			path: urlProvider.selected(semester.year, semester.month),
			controllers: ['SelectionCtrl']
		};

		$scope.$watch('selection', function(selection){
			if (selection){
				selectedItem.name = 'Selected (' + selection.numberOfCourses() + ')';
			}
		}, true);

		$scope.items = [catalogItem, selectedItem];
		$scope.selectedItem = catalogItem;
		function updateSelection(route){
			_($scope.items).each(function(item){
				if (item.path == $location.path() || (route && _.contains(item.controllers, route.controller))){
					$scope.selectedItem = item;
				}
			});
		}
		updateSelection();
		$scope.$on('$routeChangeSuccess', function (ev, current, prev) {
			updateSelection(current);
		});

		$scope.click = function(item){
			$scope.selectedItem = item;
			$location.path(item.path).search({});
		};
	});
}]);

})(angular, app);

