'use strict';

(function(angular, app, undefined){

app.factory('Selection', ['$q', '$cookieStore', 'currentSemesterPromise',
			'currentCourses', 'scheduleValidator', 'Utils', '$timeout',
			'SavedSelection', 'SectionTime',
			function($q, $cookieStore, currentSemesterPromise,
					 currentCourses, scheduleValidator, Utils, $timeout,
					 SavedSelection, SectionTime){
	var storageKeyPromise = currentSemesterPromise.then(function(semester){
		return 'selection:' + semester.id;
	});

	function Selection(courseIdsToSectionIds, blockedTimes, id){
		this.id = id || null; // not created unless saved
		this.courseIdsToSectionIds = courseIdsToSectionIds || {};
		this.blockedTimes = blockedTimes || {};
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
			var data = {};
			try {
				data = angular.fromJson(str);
			} catch(err) {
				console.error('Failed to load selection: ', err, 'data: ', str);
			}
			return new Selection(data.selection, data.blockedTimes, data.id);
		},
		loadCurrent: function(){
			return storageKeyPromise.then(function(key){
				var selection;
				try {
					selection = Selection.deserialize($cookieStore.get(key))
				} catch(e) {
					selection = new Selection();
					console.warn('Failed to load selection, using empty one: ', e);
				}
				return selection;
			});
		},
		loadCurrentWithId: function(){
			var deferred = $q.defer();
			Selection.current.then(function(selection){
				selection.save().then(function(){
					deferred.resolve(selection);
				});
			});
			return deferred.promise;
		},
		loadById: function(id){
			return SavedSelection.get(id).then(function(savedSelection){
				console.log(savedSelection);
				var sel = new Selection(savedSelection.selection, {}, savedSelection.id);
				_.each(savedSelection.blocked_times, function(key){
					sel.setBlockedTime(key);
				});
				return sel;
			});
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
			course.is_selected = !course.is_selected;
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
			section.is_selected = !section.is_selected;
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
			return angular.toJson({
				id: this.id,
				selection: this.courseIdsToSectionIds,
				blockedTimes: this.blockedTimes,
			});
		},
		saveToServer: function(){
			var self = this;
			var savedSelection = new SavedSelection({
				selection: self.courseIdsToSectionIds,
				blocked_times: self.blockedTimes
			});

			return savedSelection.save().then(function(savedSelection){
				self.id = savedSelection.id;
				return self;
			});
		},
		save: function(){
			var self = this;
			var deferred = $q.defer();
			storageKeyPromise.then(function(key){
				$cookieStore.put(key, self.serialize());

				self.saveToServer().then(function(selection){
					deferred.resolve(self);
				});
			});
			return deferred.promise;
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
			this.blockedTimes = {};
		},
		setBlockedTime: function(key){ // key = 'DOW_Hour:Minute:Second'
			var day_time = key.split('_');
			var times = day_time[1].split(':');
			var hour = parseInt(times[0], 10),
				min = parseInt(times[1], 10),
				sec = parseInt(times[2], 10);
			this.blockedTimes[key] = {
				days_of_the_week: [day_time[0]],
				start: day_time[1],
				end: [ // we only care about half hour blocks
					min === 0 ? hour : hour + 1,
					min === 0 ? min + 29 : min,
					sec
				].join(':')
			};
		},
		allBlockedTimes: function(){
			var obj = {};
			_.each(this.blockedTimes, function(sectionTimeObj, key){
				obj[key] = new SectionTime(sectionTimeObj);
			});
			return obj;
		},
		getBlockedTime: function(key){
			return new SectionTime(this.blockedTimes[key]);
		},
		removeBlockedTime: function(key){
			delete this.blockedTimes[key];
		}
	});

	Selection.current = Selection.loadCurrent();

	return Selection;
}]);

})(angular, app);

