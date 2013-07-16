'use strict';


describe("Controllers", function(){
	var scope, icalUrl;
	beforeEach(inject(function($rootScope, ICAL_URL){
		scope = $rootScope.$new();
		icalUrl = ICAL_URL;
	}));

	describe("SelectionCtrl", function(){
		var controller, CourseFetcher, schedulePresenter, searchOptions;
		var semesterDeferred, selectionDeferred, coursesDeferred, schedulesDeferred;
		beforeEach(inject(function($injector, $controller, $q, Selection){
			searchOptions = $injector.get('searchOptions');
			schedulesDeferred = $q.defer();
			coursesDeferred = $q.defer();
			semesterDeferred = $q.defer();
			selectionDeferred = $q.defer();
			schedulePresenter = jasmine.createSpy('schedulePresenter').andReturn(schedulesDeferred.promise);
			CourseFetcher = jasmine.createSpy('CourseFetcher').andReturn(coursesDeferred.promise);
			Selection.current = selectionDeferred.promise;
			controller = $controller('SelectionCtrl', {
				$scope: scope,
				currentSemesterPromise: semesterDeferred.promise,
				CourseFetcher: CourseFetcher,
				Selection: Selection,
				schedulePresenter: schedulePresenter,
				searchOptions: searchOptions
			});
		}));

		it("should disable the search bar", function(){
			expect(searchOptions.visible).not.toBeTruthy();
		});

		it("should set the courses on the scope", function(){
			expect(scope.courses).toEqual([]);
		});

		it("should sets the empty text on the scope", function(){
			expect(scope.emptyText).toBeTruthy();
		});

		describe("when the current semester and selection are resolved with an empty selection", function(){
			var selection;
			beforeEach(inject(function($rootScope, Semester, Selection){
				selection = new Selection({});
				spyOn(selection, 'apply');
				semesterDeferred.resolve(new Semester({id: 12}));
				selectionDeferred.resolve(selection);
				$rootScope.$apply();
			}));

			it("should query for its courses in its selection", function(){
				expect(CourseFetcher).not.toHaveBeenCalled();
			});
		});

		describe("when the current semester and selection are resolved", function(){
			var selection;
			beforeEach(inject(function($rootScope, Semester, Selection){
				selection = new Selection({2: [3], 4: [5]});
				spyOn(selection, 'apply');
				semesterDeferred.resolve(new Semester({id: 12}));
				selectionDeferred.resolve(selection);
				$rootScope.$apply();
			}));

			describe("tapping on the clear selection button", function(){
				beforeEach(inject(function($rootScope){
					scope.clickClearSelection();
					$rootScope.$apply();
				}));

				it("should clear the selection", function(){
					expect(selection.numberOfCourses()).toEqual(0);
				});
			});

			it("should query for its courses in its selection", function(){
				expect(CourseFetcher).toHaveBeenCalledWith({
					semester_id: 12,
					id: ['2', '4']
				});
			});

			it("should show the show clear button", function(){
				expect(scope.showClearButton()).toBeTruthy();
			});

			describe("when the courses query is resolved", function(){
				var courses;
				beforeEach(inject(function($rootScope, Course){
					courses = [new Course()];
					coursesDeferred.resolve(courses);
					$rootScope.$apply();
				}));

				it("should updates the courses on the scope", function(){
					expect(scope.courses).toEqual(courses);
				});

				it("should apply the current selection to the courses", function(){
					expect(selection.apply).toHaveBeenCalledWith(courses);
				});

				describe("when clicking clear selection button", function(){
					beforeEach(inject(function($rootScope){
						spyOn(selection, 'clear');
						spyOn(selection, 'save');
						scope.clickClearSelection();
						$rootScope.$apply();
					}));

					it("should clear the selection", function(){
						expect(selection.clear).toHaveBeenCalled();
					});

					it("should apply the selection to the courses on the scope", function(){
						expect(selection.apply).toHaveBeenCalledWith(scope.courses);
					});

					it("should save the selection", function(){
						expect(selection.save).toHaveBeenCalled();
					});
				});

				describe("when clicking a course", function(){
					var clickedCourse, updateCourseDeferred;
					beforeEach(inject(function($rootScope, $q, Course){
						updateCourseDeferred = $q.defer();
						spyOn(selection, 'updateCourse').andReturn(updateCourseDeferred.promise);
						spyOn(selection, 'save');
						clickedCourse = new Course();
						scope.clickCourse(clickedCourse);
					}));

					it("should call updateCourse for the selection", function(){
						expect(selection.updateCourse).toHaveBeenCalledWith(clickedCourse);
					});

					describe("when the selection has been updated successfully", function(){
						beforeEach(inject(function($rootScope){
							updateCourseDeferred.resolve();
							$rootScope.$apply();
						}));

						it("should save the selection", function(){
							expect(selection.save).toHaveBeenCalled();
						});

						it("should apply the selection to the scope's courses", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});

					describe("when the selection has failed to update", function(){
						beforeEach(inject(function($rootScope){
							updateCourseDeferred.reject();
							$rootScope.$apply();
						}));

						it("should apply the selection to revert the user's change", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});
				});

				describe("when clicking a section", function(){
					var clickedCourse, clickedSection, updateSectionDeferred;
					beforeEach(inject(function($rootScope, $q, Course, Section){
						updateSectionDeferred = $q.defer();
						spyOn(selection, 'updateSection').andReturn(updateSectionDeferred.promise);
						spyOn(selection, 'save');
						clickedCourse = new Course();
						clickedSection = new Section();
						scope.clickSection(clickedCourse, clickedSection);
					}));

					it("should call updateSection", function(){
						expect(selection.updateSection).toHaveBeenCalledWith(clickedCourse, clickedSection);
					});

					describe("when the selection has been updated successfully", function(){
						beforeEach(inject(function($rootScope){
							updateSectionDeferred.resolve();
							$rootScope.$apply();
						}));

						it("should save the selection", function(){
							expect(selection.save).toHaveBeenCalled();
						});

						it("should apply the selection to the scope's courses", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});

					describe("when the selection has failed to update", function(){
						beforeEach(inject(function($rootScope){
							updateSectionDeferred.reject();
							$rootScope.$apply();
						}));

						it("should apply the selection to revert the user's change", function(){
							expect(selection.apply).toHaveBeenCalledWith(scope.courses);
						});
					});
				});

				describe("when blocking a course", function(){
					var time;
					beforeEach(inject(function($rootScope, Time){
						time = new Time(12, 0, 0);
						scope.toggleBlockableTime(time, 'Monday');
						$rootScope.$apply();
					}));

					it("should mark the time as blocked", function(){
						expect(scope.isBlocked(time, 'Monday')).toBeTruthy();
					});
				});

				/* TODO: iCal link broken
				describe("when schedules are resolved with no schedules", function(){
					beforeEach(inject(function($rootScope){
						scope.ical_url = 'foo';
						schedulesDeferred.resolve([]);
						$rootScope.$apply();
					}));

					it("should remove the ical url to the scope", function(){
						expect(scope.ical_url).toBeFalsy();
					});
				});
				*/

				describe("when schedules are resolved", function(){
					beforeEach(inject(function($rootScope){
						schedulesDeferred.resolve([{crns: [2, 4]}, {crns: [2]}]);
						$rootScope.$apply();
					}));

					/* TODO: iCal link broken
					it("should set the ical url to the scope", function(){
						expect(scope.ical_url).toEqual(icalUrl + '?crn=2&crn=4');
					});
					*/

					describe("when tapping the left arrow key", function(){
						beforeEach(function(){
							scope.scheduleIndex = 1;
							scope.keyDown($.Event('keydown', {keyCode: 37}));
							scope.$apply();
						});

						it("should decrement the schedule index", function(){
							expect(scope.scheduleIndex).toEqual(0);
						});

						describe("tapping the left arrow when at the beginning", function(){
							beforeEach(function(){
								scope.keyDown($.Event('keydown', {keyCode: 37}));
								scope.$apply();
							});

							it("should not decrement the schedule index", function(){
								expect(scope.scheduleIndex).toEqual(0);
							});
						});
					});

					describe("when tapping the right arrow key", function(){
						beforeEach(function(){
							scope.scheduleIndex = 0;
							scope.keyDown($.Event('keydown', {keyCode: 39}));
							scope.$apply();
						});

						it("should decrement the schedule index", function(){
							expect(scope.scheduleIndex).toEqual(1);
						});

						describe("tapping the right arrow when at the end", function(){
							beforeEach(function(){
								scope.keyDown($.Event('keydown', {keyCode: 39}));
								scope.$apply();
							});

							it("should not increment the schedule index", function(){
								expect(scope.scheduleIndex).toEqual(1);
							});
						});
					});
				});
			});
		});
	});
});
