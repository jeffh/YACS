'use strict';

(function(angular, app, undefined){

app.factory('Semester', function(ModelFactory, Utils){
	var url = Utils.URL('/api/4/semesters/');
	/*
	 * name: "Spring 2013",
	 * year: 2013,
	 * date_updated: "2013-03-05T22:34:57.904120",
	 * ref: "http://sis.rpi.edu/reg/zs201301.htm",
	 * id: 2,
	 * month: 1
	 */
	var Semester = ModelFactory('Semester', {
		query: url,
		get: url
	});
	angular.extend(Semester, {
		latest: function(){
			return Semester.query().then(function(semesters){
				return semesters[0];
			});
		}
	});
	return Semester;
});

app.factory('currentSemesterPromise', function(Semester, $rootScope, $q){
	var deferred = $q.defer();
	$rootScope.$on('$routeChangeSuccess', function(event, current, previous){
		var year = current.params.year,
			month = current.params.month;
		if (year && month){
			Semester.query({
				year: current.params.year,
				month: current.params.month
			}).then(function(semesters){
				deferred.resolve(semesters[0]);
			});
		} else {
			Semester.latest().then(function(semester){
				deferred.resolve(semester);
			});
		}
	});
	return deferred.promise;
});

})(angular, app);

