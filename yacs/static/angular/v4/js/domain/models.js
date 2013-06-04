'use strict';

(function(document, angular, app, undefined){

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

app.factory('Course', function(ModelFactory, Section, tagger, Utils, conflictor){
	var url = Utils.URL('/api/4/courses/');
	/*
	 * description: "",
	 * is_comm_intense: false,
	 * min_credits: 0,
	 * grade_type: "Satisfactory/Unsatisfactory",
	 * number: 1010,
	 * max_credits: 0,
	 * prereqs: "",
	 * department_id: 38,
	 * id: 923,
	 * name: "ORAL COMM FOR TA'S"
	 *
	 * Added:
	 * sections: []
	 * department: {}
	 * tags: []
	 * is_selected: false
	 * notes: []
	 * conflicts: []
	 */
	var Course = ModelFactory('Course', {
		defaults: {
			sections: [],
			department: {},
			tags: [],
			is_selected: false,
			conflicts: []
		},
		query: url,
		get: url
	});
	angular.extend(Course.prototype, {
		seatsLeft: function(){
			// it's possible for seatsTaken() > seatsTotal(),
			// so we need to compute this manually
			return _(this.sections).reduce(function(num, section){
				return Math.max(section.seats_total - section.seats_taken, 0) + num;
			}, 0);
		},
		seatsTaken: function(){
			return _(this.sections).reduce(function(num, section){
				return section.seats_taken + num;
			}, 0);
		},
		seatsTotal: function(){
			return _(this.sections).reduce(function(num, section){
				return section.seats_total + num;
			}, 0);
		},
		sectionsText: function(){
			var n = this.sections.length;
			return n + Utils.pluralize(' section', n);
		},
		seatsLeftText: function(){
			var n = Math.max(this.seatsLeft(), 0);
			return n + Utils.pluralize(' seat', n);
		},
		sectionTypes: function(){
			return _(this.sections).chain().pluck('section_times').flatten().pluck('kind').uniq().value();
		},
		creditsText: function(){
			if (this.min_credits === this.max_credits) {
				return this.min_credits + Utils.pluralize(' credit', this.min_credits);
			}
			return this.min_credits + ' - ' + this.max_credits + ' credits';
		},
		computeProperties: function(){
			var self = this;
			this.conflicts = conflictor.courseConflictsAmongAllSections(this);
			_(this.sections).each(function(section){
				section.computeProperties();
				var sectionNames = _.difference(section.allConflicts, self.conflicts);
				if (section.is_selected || _.isEqual(sectionNames, [])){
					section.conflicts = sectionNames;
				} else {
					section.conflicts = angular.copy(section.allConflicts);
				}
			});
			this.tags = tagger(this);
			this.notes = _(this.sections).chain().pluck('notes').uniq().value();
		}
	});
	return Course;
});

app.factory('Department', function(ModelFactory, Utils){
	var url = Utils.URL('/api/4/departments/');
	/*
	 * code: "ADMN",
	 * id: 38,
	 * name: "Administration"
	 */
	var Department = ModelFactory('Department', {
		query: url,
		get: url
	});
	return Department;
});


app.factory('Time', function(){
	function Time(str){
		var parts = _(str.split(':')).map(function(i){ return parseInt(i, 10); });
		this.hour = parts[0];
		this.minute = parts[1];
		this.second = parts[2];
		this.totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
	}
	Time.prototype = {};
	angular.extend(Time.prototype, {
		isOnTheHour: function(){
			return this.minute === 0 && this.second === 0;
		},
		isAM: function(){
			return this.hour < 12;
		},
		APM: function(){
			return (this.isAM() ? 'am' : 'pm');
		},
		getLocalHour: function(){
			var hour = this.hour;
			if (hour == 0 || hour == 12) {
				return 12;
			}
			return (hour > 12 ? hour - 12 : hour);
		},
		text: function(options){
			options = _.extend({
				showAPM: true
			}, options);

			var times = [];
			times.push(this.getLocalHour());
			if (!this.isOnTheHour()){
				times.push(':');
				times.push(this.minute);
			}
			if (options.showAPM) {
				times.push(this.APM());
			}
			return times.join('');
		}
	});
	return Time;
});

app.factory('SectionTime', function(Time){
	function SectionTime(attributes){
		angular.extend(this, attributes);
	}
	SectionTime.prototype = {};
	angular.extend(SectionTime.prototype, {
		text: function(){
			var start = new Time(this.start);
			var end = new Time(this.end);
			return [
				start.text({showAPM: false}),
				end.text()
			].join('-');
		},
		startTimeInSeconds: function(){
			return new Time(this.start).totalSeconds;
		},
		endTimeInSeconds: function(){
			return new TIme(this.end).totalSeconds;
		}
	});
	return SectionTime;
});

app.factory('Section', function(ModelFactory, SectionTime, Utils){
	var url = Utils.URL('/api/4/sections/');
	/*
	 * course_id: 1,
	 * seats_total: 50,
	 * crosslisted_id: null,
	 * semester_id: 1,
	 * id: 1,
	 * notes: "",
	 * section_times: [
	 *	   {
	 *	   start: "10:00:00",
	 *	   kind: "LEC",
	 *	   end: "11:50:00",
	 *	   location: "",
	 *	   instructor: "Zhang",
	 *	   section_id: 1,
	 *	   days_of_the_week: [
	 *		  "Monday",
	 *		  "Thursday"
	 *	   ]
	 *	   }
	 * ],
	 * crn: 95148,
	 * number: "01",
	 * seats_taken: 40
	 *
	 * added:
	 * is_selected: false
	 * conflicts: [] // conflicts only for this section and not the course (computed by course)
	 * allConflicts: [] // all conflicts
	 */
	var Section = ModelFactory('Section', {
		defaults: {
			is_selected: false,
			allConflicts: [],
			conflicts: []
		},
		query: url,
		get: url
	});
	var superInit = Section.prototype.initialize;
	angular.extend(Section.prototype, {
		initialize: function(){
			superInit.apply(this, arguments);
			this.section_times = _(this.section_times).map(function(time){
				return new SectionTime(time);
			});
		},
		seatsLeft: function(){
			return this.seats_total - this.seats_taken;
		},
		seatsLeftText: function(){
			var n = Math.max(this.seatsLeft(), 0);
			return n + Utils.pluralize(' seat', n);
		},
		instructorsText: function(){
			var instructors = _(this.section_times).chain().pluck('instructor').uniq().value();
			return instructors.join(', ');
		},
		numberText: function(){
			var str = parseInt(this.number, 10);
			return (isNaN(str) ? this.number : str);
		},
		hasMultipleTimesPerDay: function(){
			return _.some(this.times, function(time){
				return time.count > 1;
			});
		},
		computeProperties: function(){
			this.times = this._generateDayTimes();
		},
		_generateDayTimes: function(){
			var times = [];
			var days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
			var dowToSectionTime = {};
			_(days_of_the_week).each(function(dow){
				dowToSectionTime[dow] = [];
			});
			_(this.section_times).each(function(section_time){
				_(section_time.days_of_the_week).each(function(dow){
					dowToSectionTime[dow].push(section_time);
				});
			});
			_(days_of_the_week).each(function(dow){
				times.push({
					day_of_the_week: dow.substr(0, 3),
					count: dowToSectionTime[dow].length,
					section_times: _.sortBy(dowToSectionTime[dow], function(section_time){
						return section_time.startTimeInSeconds();
					})
				});
			});
			return times;
		}
	});
	return Section;
});

app.factory('Conflict', function(ModelFactory, Utils){
	var url = Utils.URL('/api/4/conflicts/');
	/*
	 * id: 1
	 * conflicts: []
	 */
	var Conflict = ModelFactory('Conflict', {
		get: url,
		query: url
	});
	angular.extend(Conflict.prototype, {
		conflictsWith: function(id){
			return _.contains(this.conflicts, id);
		}
	});
	return Conflict;
});

app.factory('CourseFetcher', function($q, Course, Department, Section, Utils){
	return function(filters){
		var deferred = $q.defer();
		var deptPromise = Department.query({semester_id: filters.semester_id});
		var coursePromise = Course.query(filters);
		$q.all([deptPromise, coursePromise]).then(function(values){
			var departments = values[0];
			var courses = values[1];
			var idToDept = Utils.hashById(departments);
			var idToCourse = Utils.hashById(courses);
			_(courses).each(function(course){
				course.department = idToDept[course.department_id];
				course.sections = [];
			});

			var sectionPromise = Section.query({
				semester_id: filters.semester_id,
				course_id: _(idToCourse).chain().keys().uniq().value()
			});
			sectionPromise.then(function(sections){
				_(sections).each(function(section){
					idToCourse[section.course_id].sections.push(section);
				});
				_(courses).each(function(course){
					course.computeProperties();
					course.sections = _.sortBy(course.sections, 'number');
				});
				deferred.resolve(courses);
			}, function(error){
				deferred.reject(error);
			});
		}, function(error){
			deferred.reject(error);
		});

		return deferred.promise;
	};
});

app.factory('CourseSearch', function(){
	var contains = function(string, substring){
		return string.indexOf(substring) >= 0;
	};
	return function(courses, query){
		var words = _.compact(query.toLowerCase().split(' '));
		return _(courses).filter(function(course){
			var courseName = course.name.toLowerCase();
			var deptCode = course.department.code.toLowerCase();
			return _.every(words, function(word){
				return (
					contains(courseName, word) ||
					contains(deptCode, word) ||
					contains(String(course.number), word)
				);
			});
		});
	};
});

app.factory('DelayTrigger', function($timeout){
	return function(fn, timeout){
		var timer = null;
		return function(){
			if (timer){
				$timeout.cancel(timer);
				timer = null;
			}
			timer = $timeout(function(){
				timer = null;
				fn();
			}, timeout);
		};
	};
});

app.service('scheduleValidator', function($q, Conflict, Semester, Section, Time, Utils, currentSemesterPromise){
	var conflictsDeferred = $q.defer();
	var sectionsDeferred = $q.defer();
	currentSemesterPromise.then(function(semester){
		Conflict.query({semester_id: semester.id}).then(function(conflicts){
			var conflictMap = Utils.hashById(conflicts);
			conflictsDeferred.resolve(conflictMap);
		}, _.bind(conflictsDeferred.reject, conflictsDeferred));
		Section.query({semester_id: semester.id}).then(function(sections){
			var idToSection = Utils.hashById(sections);
			sectionsDeferred.resolve(idToSection);
		}, _.bind(sectionsDeferred.reject, sectionsDeferred));
	});
	this.promise = $q.all([conflictsDeferred.promise, sectionsDeferred.promise]);

	// fast to check, but misses cyclic conflicts
	this.conflictsWith = function(courseIdsToSectionIds, sectionId){
		return this.promise.then(function(values){
			var conflictMap = values[0];
			var idToSection = values[1];
			var lastConflict = null;
			_(courseIdsToSectionIds).some(function(selectedSectionIds, courseId){
				return _(selectedSectionIds).all(function(sid){
					var conflict = [];
					if (conflictMap[sid].conflictsWith(sectionId)){
						conflict = {
							selectionSection: idToSection[sid],
							section: idToSection[sectionId]
						};
						lastConflict = conflict;
					}
					return conflict;
				});
			});
			return lastConflict;
		});
	};

	// slower, but checks for cyclic conflicts
	this.isValid = function(courseIdsToSectionIds){
		return this.computeSchedules(courseIdsToSectionIds, 1).then(function(schedules){
			return schedules.length;
		});
	};
	this.computeSchedules = function(courseIdsToSectionIds, num){
		var self = this;
		var deferred = $q.defer();
		var courseIds = _(courseIdsToSectionIds).keys();
		var sectionIds = _(courseIdsToSectionIds).chain().values().flatten().uniq().value();
		this.promise.then(function(values){
			var conflicts = values[0];
			var idToSections = values[1];
			var sectionDomains = _(courseIdsToSectionIds).chain(
			).values().map(function(sectionIds){
				return _.map(sectionIds, function(id){
					return idToSections[id];
				});
			}).value();

			var possibleSchedules = Utils.product(sectionDomains);
			var validSchedules = [];
			_(possibleSchedules).all(function(schedule){
				if (self._isValidSchedule(schedule)){
					validSchedules.push(_.object(courseIds, schedule));
				}
				return !num || validSchedules.length < num;
			});
			deferred.resolve(validSchedules);
		}, function(err){
			deferred.reject(err);
		});
		return deferred.promise;
	};

	this._isValidSchedule = function(schedule){ // schedule = array of sections
		var self = this;
		return _(schedule).all(function(section1, i){
			return _(schedule).all(function(section2, j){
				if (i >= j) {
					return true; // continue
				}

				return !self._areSectionsConflicted(section1, section2);
			});
		});
	};

	this._areSectionsConflicted = function(section1, section2){
		var self = this;
		return _(section1.section_times).some(function(time1){
			return _(section2.section_times).some(function(time2){
				return self._areTimesConflicted(time1, time2);
			});
		});
	};

	this._areTimesConflicted = function(time1, time2){
		var dows = _(time1.days_of_the_week).intersection(time2.days_of_the_week);
		var startTime1 = new Time(time1.start).totalSeconds;
		var startTime2 = new Time(time2.start).totalSeconds;
		var endTime1 = new Time(time1.end).totalSeconds;
		var endTime2 = new Time(time2.end).totalSeconds;
		return dows.length && (
			(startTime1 <= startTime2 && startTime2 <= endTime1) ||
			(startTime2 <= startTime1 && startTime1 <= endTime2) ||
			(startTime1 <= endTime2 && endTime2 <= endTime1) ||
			(startTime2 <= endTime1 && endTime1 <= endTime2)
		);
	};
});

app.factory('Selection', function($q, $cookieStore, Semester, scheduleValidator, Utils){
	var storageKeyPromise = Semester.latest().then(function(semester){
		return 'selection:' + semester.id;
	});

	function Selection(courseIdsToSectionIds){
		this.courseIdsToSectionIds = courseIdsToSectionIds || {};
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
				deferred.resolve(selection);
			});
			return deferred.promise;
		}
	});

	angular.extend(Selection.prototype, {
		copy: function(){
			return new Selection(angular.copy(this.courseIdsToSectionIds));
		},
		_eachSection: function(courses, iterator){
			var self = this;
			_(courses).each(function(course){
				_(course.sections).each(function(section){
					iterator(course, section);
				});
			});
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
		markAllConflicted: function(courses){
			var self = this;
			var promises = [];
			var idToCourse = Utils.hashById(courses);
			var idToSection = Utils.hashById(_.flatten(_.pluck(courses, 'sections')));
			this._eachSection(courses, function(course, section){
				section.allConflicts = [];
				if (section.is_selected) {
					return;
				}
				var deferred = $q.defer();
				var promise = scheduleValidator.conflictsWith(self.courseIdsToSectionIds, section.id);
				function error(err){ deferred.reject(err); }
				promise.then(function(conflict){
					if (conflict) {
						var conflictedCourse = idToCourse[conflict.selectionSection.course_id];
						uniquePush(section.allConflicts, conflictedCourse.name);
						deferred.resolve();
						return;
					}
					var clone = self.copy();
					clone._addSection(course, section);
					promise = scheduleValidator.isValid(clone.courseIdsToSectionIds);
					promise.then(function(isValid){
						if (!isValid){
							uniquePush(section.allConflicts, 'selected courses');
						}
						deferred.resolve();
					}, error);
				}, error);

				promises.push(deferred.promise);
			});
			return $q.all(promises).then(function(values){
				_(courses).each(function(course){
					course.computeProperties();
				});
				return values;
			});
		},
		apply: function(courses){
			this.selectCoursesAndSections(courses);
			return this.markAllConflicted(courses);
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
			var lastSectionId = null;
			var self = this;
			var conflictPromises = _(addedSectionIds).map(function(sectionId){
				return scheduleValidator.conflictsWith(sectionId);
			});
			$q.all(conflictPromises).then(function(values){
				values = _.compact(values);
				if (values.length){
					console.log('invalid', lastSectionId);
					deferred.reject(lastSectionId);
					return;
				}
				self.saveCheckpoint();
				fn();
				var promise = scheduleValidator.isValid(self.courseIdsToSectionIds);
				promise.then(function(isValid){
					if (isValid){
						deferred.resolve(null);
					} else {
						self.restoreToCheckpoint();
						console.log('invalid');
						deferred.reject(null);
					}
				});
			});
			return deferred.promise;
		},
		updateCourse: function(course){
			var self = this;
			if (course.is_selected) {
				var hasSelectedASection = false;
				var sectionIds = _(course.sections).chain().filter(function(section){
					if (!self._isFull(section)){
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
		}
	});
	Selection.current = Selection.load();
	return Selection;
});

})(document, angular, app);

