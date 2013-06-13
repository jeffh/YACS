'use strict';

describe("Domain", function(){
	describe("Models", function(){
		describe("Selection", function(){
			var Selection, selection;
			beforeEach(inject(function($injector){
				Selection = $injector.get('Selection');
				selection = new Selection();
			}));

			it("should supports copied selections", function(){
				var anotherSelection = selection.copy();
				selection.courseIdsToSectionIds[1] = [2, 3];
				expect(anotherSelection.serialize()).not.toEqual(selection.serialize());
			});

			describe("with an empty selection", function(){
				describe("courseIds", function(){
					it("should return no course ids", function(){
						expect(selection.courseIds()).toEqual([]);
					});
				});

				describe("numberOfCourses", function(){
					it("should return 0", function(){
						expect(selection.numberOfCourses()).toEqual(0);
					});
				});
			});

			describe("with an existing selection", function(){
				beforeEach(function(){
					selection = new Selection({1: [2, 3], 4: [5]});
				});

				describe("clear", function(){
					beforeEach(function(){
						selection.clear()
					});

					it("should have no selected courses", function(){
						expect(selection.numberOfCourses()).toEqual(0);
					});

					it("should ", function(){
						expect(selection.serialize()).toEqual('{}');
					});
				});
			});
		});
	});
});
