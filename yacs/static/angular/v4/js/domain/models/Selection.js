'use strict';

(function(angular, app, undefined){

app.factory('Selection', function($q, $cookieStore, currentSemesterPromise, currentCourses, scheduleValidator, Utils, $timeout){
	var storageKeyPromise = currentSemesterPromise.then(function(semester){
		return 'selection:' + semester.id;
	});

	function Selection(courseIdsToSectionIds, blockedTimes){
		this.courseIdsToSectionIds = courseIdsToSectionIds || {};
		this.blockedTimes = {};
	}
	function uniquePush(arr, item){
		if (!_.contains(arr, item)){
			arr.push(item);
		}
		return arr;
	}
	Selection.prototype = {};
	angular.extend(Selection, {
		deserialize: function(str){
			return new Selection(angular.fromJson(str));
		},
		load: function(){
			var deferred = $q.defer();
			storageKeyPromise.then(function(key){
				var selection;
				try {
					selection = Selection.deserialize($cookieStore.get(key))
				} catch(e) {
					selection = new Selection();
					console.log('Failed to load selection, using empty one');
				}
				window.selection = selection;
				deferred.resolve(selection);
			});
			return deferred.promise;
		}
	});

	angular.extend(Selection.prototype, {
		copy: function(){
			return new Selection(angular.copy(this.courseIdsToSectionIds));
		},
		courseIds: function(){
			return _.keys(this.courseIdsToSectionIds);
		},
		numberOfCourses: function(){
			return this.courseIds().length;
		},
		_eachSection: function(courses, iterator){
			var self = this;
			_(courses).each(function(course){
				_(course.sections).each(function(section){
					iterator(course, section);
				});
			});
		},
		schedules: function(blockedTimes){
			return scheduleValidator.computeSchedules(this.courseIdsToSectionIds, blockedTimes);
		},
		selectCoursesAndSections: function(courses){
			var self = this;
			this._eachSection(courses, function(course, section){
				course.is_selected = false;
				section.is_selected = false;
			});
			this._eachSection(courses, function(course, section){
				var sectionIdsForCourse = self.courseIdsToSectionIds[course.id];
				if (_(sectionIdsForCourse).contains(section.id)){
					section.is_selected = true;
					course.is_selected = true;
				}
			});
		},
		markAllConflicted: function(listedCourses){
			var self = this;
			var deferred = $q.defer();
			currentCourses.then(function(allCourses){
				var promises = [];
				var idToCourse = Utils.hashById(allCourses);
				self._eachSection(listedCourses, function(course, section){
					section.allConflicts = [];
					if (section.is_selected) {
						return;
					}
					var deferred = $q.defer();
					var promise = scheduleValidator.conflictsWith(self.courseIdsToSectionIds, section.id);
					function error(err){ deferred.reject(err); }
					promise.then(function(conflict){
						var conflictedCourse = null;
						if (conflict) {
							conflictedCourse = idToCourse[conflict.selectionSection.course_id];
						}
						var clone = self.copy();
						clone._addSection(course, section);
						promise = scheduleValidator.isValid(clone.courseIdsToSectionIds);
						promise.then(function(isValid){
							if (!isValid){
								uniquePush(section.allConflicts, conflictedCourse ? conflictedCourse.name : 'selected courses');
							}
							deferred.resolve();
						}, error);
					}, error);

					promises.push(deferred.promise);
				});
				$q.all(promises).then(function(values){
					_(listedCourses).each(function(course){
						course.computeProperties();
					});
					deferred.resolve(values);
				});
			});
			return deferred.promise;
		},
		apply: function(courses){
			this.selectCoursesAndSections(courses);
			var self = this;
			var deferred = $q.defer();
			$timeout(function(){
				self.markAllConflicted(courses).then(function(values){
					deferred.resolve(values);
				}, function(err){
					deferred.reject(err);
				});
			}, 100);
			return deferred.promise;
		},
		containsCourse: function(course){
			var courseIds = _.keys(this.courseIdsToSectionIds)
			return _(courseIds).contains(course.id);
		},
		containsSection: function(section){
			var sectionIds = this.courseIdsToSectionIds[section.course_id]
			return _(sectionIds).contains(section.id);
		},
		saveCheckpoint: function(){
			this._checkpoint = angular.copy(this.courseIdsToSectionIds);
		},
		restoreToCheckpoint: function(){
			if (this._checkpoint){
				this.courseIdsToSectionIds = this._checkpoint;
				this._checkpoint = null;
			}
		},
		_updateAndValidate: function(fn, addedSectionIds){
			var deferred = $q.defer();
			var self = this;
			self.saveCheckpoint();
			fn();
			var promise = scheduleValidator.isValid(self.courseIdsToSectionIds);
			promise.then(function(isValid){
				if (isValid){
					deferred.resolve(null);
				} else {
					self.restoreToCheckpoint();
					deferred.reject(null);
				}
			});
			return deferred.promise;
		},
		updateCourse: function(course){
			var self = this;
			if (course.is_selected) {
				var hasSelectedASection = false;
				var sectionIds = _(course.sections).chain().filter(function(section){
					if (!self._isFull(section) && _.isEmpty(section.allConflicts)){
						section.is_selected = true;
						hasSelectedASection = true;
					}
					return section.is_selected;
				}).pluck('id').value();

				if (!hasSelectedASection) {
					sectionIds = _(course.sections).chain().each(function(section){
						section.is_selected = true;
					}).pluck('id').value();
				}

				return this._updateAndValidate(function(){
					self.courseIdsToSectionIds[course.id] = sectionIds;
				}, sectionIds);
			} else {
				_(course.sections).each(function(section){
					section.is_selected = false;
				});
				this.courseIdsToSectionIds[course.id] = [];
				var deferred = $q.defer();
				deferred.resolve(null);
				return deferred.promise;
			}
		},
		_addSection: function(course, section){
			this.courseIdsToSectionIds[course.id] = this.courseIdsToSectionIds[course.id] || [];
			uniquePush(this.courseIdsToSectionIds[course.id], section.id);
		},
		updateSection: function(course, section){
			var self = this;
			if (section.is_selected){
				course.is_selected = true;
				return this._updateAndValidate(function(){
					self._addSection(course, section);
				}, [section.id]);
			} else {
				if (!this._hasSelectedSections(course)){
					course.is_selected = false;
				}
				this.courseIdsToSectionIds[course.id] = _(this.courseIdsToSectionIds[course.id] || []).without(section.id);
				var deferred = $q.defer();
				deferred.resolve(null);
				return deferred.promise;
			}
		},
		serialize: function(){
			var self = this;
			_(this.courseIdsToSectionIds).each(function(sectionIds, courseId){
				if (!sectionIds || !sectionIds.length){
					delete self.courseIdsToSectionIds[courseId];
				}
			});
			return angular.toJson(this.courseIdsToSectionIds);
		},
		save: function(){
			var self = this;
			return storageKeyPromise.then(function(key){
				$cookieStore.put(key, self.serialize());
			});
		},
		_isFull: function(section){
			return section.seatsLeft() <= 0;
		},
		_hasSelectedSections: function(course){
			return _(course.sections).some(function(section){
				return section.is_selected;
			});
		},
		clear: function(){
			this.courseIdsToSectionIds = {};
		}
	});
	Selection.current = Selection.load();
	return Selection;
});

})(angular, app);

