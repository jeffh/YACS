'use strict';

describe("Text", function(){
	describe("tagger", function(){
		var tags, course, sectionTimeTags, courseTags;

		beforeEach(inject(function(Course, tagger, kSectionTimeTags, kCourseTags){
			sectionTimeTags = kSectionTimeTags;
			courseTags = kCourseTags;
			tags = tagger;
			course = new Course({
				grade_type: '',
				sections: [{
					section_times: [
						{ kind: "UNKNOWN" },
						{ kind: "REC" },
						{ kind: "TES" },
						{ kind: "STU" },
						{ kind: "LEC" },
						{ kind: "LAB" }
					]
				}]
			});
		}));

		it("should tag by section types in a specific order (with unknowns last)", function(){
			function namesOnly(x){
				return _(x).pluck('name');
			}
			expect(namesOnly(tags(course))).toEqual(namesOnly([
				sectionTimeTags.LEC,
				sectionTimeTags.LAB,
				sectionTimeTags.REC,
				sectionTimeTags.STU,
				sectionTimeTags.TES,
				{ name: "UNKNOWN", sort_order: 9999}
			]));
		});

		describe("with a pass/fail course", function(){
			beforeEach(inject(function(Course){
				course = new Course({ grade_type: 'Satisfactory/Unsatisfactory', sections: course.sections });
			}));

			it("should include the pass/fail tag", function(){
				expect(tags(course)).toContain(courseTags.passOrFail);
			});
		});


		describe("with a communication intensive course", function(){
			beforeEach(inject(function(Course){
				course = new Course({ is_comm_intense: true });
			}));

			it("should include the communication intensive tag", function(){
				expect(tags(course)).toContain(courseTags.communicationIntensive);
			});
		});
	});
});
