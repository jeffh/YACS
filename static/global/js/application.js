(function(document, window, $, Backbone, _, undefined){

function cleanInt(text){
    return parseInt($.trim(text), 10);
}

var ItemView = Backbone.View.extend({
    tagName: 'li',
    template: null,

    initialize: function(){
        this.model.bind('change', this.render, this);
        this.model.bind('destroy', this.remove, this);
        this.template = this.options.template;
    },
    render: function(){
        console.log('rendering');
        //$(this.el).html(this.template())
        if(!this.template)
            throw 'template is null!';
        $(this.el).html(_.template(this.template, this.model.toJSON()));
        return this;
    },
    remove: function(){
        $(this.el).remove();
    }
});
window.Department = Department;
window.ItemView = ItemView;

var MarkableItemView = ItemView.extend({
    events: {
        'change input[type=checkbox]:first': 'toggleMark'
    },

    initialize: function(){
        ItemView.prototype.initialize.call(this);
    },

    checkbox: function(){
        return this.$('input[type=checkbox]:first');
    },

    mark: function(){
        //this.checkbox().attr('checked', 'checked');
        this.model.mark();
    },
    unmark: function(){
        //this.checkbox().removeAttr('checked');
        this.model.unmark();
    },
    toggleMark: function(){
        if (this.checkbox().is(':checked'))
            this.mark();
        else
            this.unmark();
    }
});


var MarkableCourseItemView = MarkableItemView.extend({
    subview_selector: null,
    initialize: function(){
        MarkableItemView.prototype.initialize.call(this);
        this.subviews = this.options.subviews || [];
        this.subview_selector = this.options.subview_selector || this.subview_selector;
    },
    add: function(view){
        this.subviews.push(view);
        this.render();
    },
    remove: function(view){
        this.subviews.remove(view);
        view.destroy();
        this.render();
    },
    render: function(){
        ItemView.prototype.render.call(this);
        var parent = this.el;
        if (this.subview_selector)
            parent = this.$(this.subview_selector);
        _.each(this.subviews, function(view){
            parent.append(view.render().el);
        });
        return this;
    }
});

var DepartmentsView = Backbone.View.extend({
    ItemView: ItemView,
    initialize: function(){
        this.semester = this.options.semester;
        this.ItemView = this.options.ItemView || ItemView;
        this.departments = this.options.departmentsList || new DepartmentList();
        this.readDepartmentsFromDOM();
        this.departments.bind('add', this.add, this);
        this.departments.bind('reset', this.addAll, this);
        this.departments.bind('all', this.render, this);
    },
    readDepartmentsFromDOM: function(){
        var self = this;
        var template = $('#department-template').html()
        self.$('li').each(function(){
            var code = $(this).find('.deptcode').text(),
                name = $(this).find('.deptname').text();
            var dept = new Department({
                code: code,
                name: name,
                semester: self.semester
            });
            new self.ItemView({
                model: dept,
                el: this,
                template: template
            }).render();
            self.departments.add(dept);
        });
    },
    add: function(dept){
        var template = $('#department-template').html();
        var view = new this.ItemView({
            model: dept,
            template: template
        });
        this.$('ul').append(view.render().el);
    },
    addAll: function(){
        this.departments.each(this.add);
    },
    render: function(){
        return this;
    }
});

var SelectedView = Backbone.View.extend({
    CourseItemView: MarkableCourseItemView,
    SectionItemView: MarkableItemView,

    initialize: function(){
        this.semester = this.options.semester;
        this.CourseItemView = this.options.CourseItemView || this.CourseItemView;
        this.SectionItemView = this.options.SectionItemView || this.SectionItemView;
        this.courses = this.options.courseList || new CourseList();
        this.sections = this.options.sectionList || new SectionList();
        this.mapping = {}; // course.id => section.crn

        this.readFromDOM();
        this.courses.bind('all', this.render, this);
        this.sections.bind('all', this.render, this);
    },
    readFromDOM: function(){
        var self = this,
            course_template = $('#selected-course-template').html(),
            section_template = $('#selected-section-template').html();

        var courses = [];
        self.$('.course').each(function(){
            var name = $.trim($(this).find('.name').html()),
                deptcode = $.trim($(this).find('.department').html()),
                number = parseInt($(this).find('.course_number').text(), 10),
                credits = $.trim($(this).find('.credits').html()),
                seats_left = parseInt($(this).find('.seats-left .number').text(), 10),
                dept = new Department({
                    code: deptcode
                }),
                cid = cleanInt($(this).find('input:first').attr('id').substr('selected_course_'.length));
            var course = new Course({
                id: cid,
                name: name,
                department: dept,
                number: number,
                credits: credits,
                seats_left: seats_left,
                semester: self.semester,
                marked: true
            });

            var $course = $(this).addClass('course');
            var sections = [];
            self.courses.add(course);
            self.mapping[course.id] = [];

            $course.find('.section').each(function(i){
                var crn = cleanInt($(this).find('.crn').text()),
                    secnum = cleanInt($(this).find('.section-number .number').html()),
                    section_seats_left = cleanInt($(this).find('.section-seats-left .number').text()),
                    is_marked = $(this).find('input[type=checkbox]:first').val();
                var section = new Section({
                    course: course,
                    crn: crn,
                    number: secnum,
                    seats_left: section_seats_left,
                    marked: is_marked ? true : false,
                    semester: self.semester
                });
                self.sections.add(section);
                self.mapping[course.id].push(section.get('crn'));
                var view = new self.SectionItemView({
                    model: section,
                    template: section_template,
                    className: 'section' + ((section_seats_left < 1) ? ' full' : '')
                });

                // if seats_left < 1: addClass 'full'
                sections.push(view);
            });
            var course_view = new self.CourseItemView({
                model: course,
                template: course_template,
                className: 'course',
                subview_selector: '.sections > ul',
                subviews: sections
            }).render();
            courses.push(course_view);
        });

        this.$('#selected_courses').html('');
        _.each(courses, function(course){
            this.$('#selected_courses').append(course.render().el);
        });
    },
    add: function(course, sections){
        var self = this;
        this.courses.add(course);
        this.mapping[course.id] = this.mapping[course.id] || [];

        var course_template = $('#selected-course-template').html(),
            section_template = $('#selected-section-template').html();
        var course_view = new this.CourseItemView({
            model: course,
            template: course_template
        });
        _.each(sections, function(section){
            self.sections.add(section);
            this.mapping[course.id].push(section.crn);
            var section_view = new this.SectionItemView({
                model: section,
                template: section_template
            });
        }, this);
    },
    render: function(){
        return this;
    }
});

var AppView = Backbone.View.extend({
    el: document.body,

    initialize: function(year, month){
        this.semester = new Semester({year: year, month: month});
        this.subview = null;
        this.viewType = null;
        this.autodetectActiveView();

        if (this.viewType !== 'selected'){
            this.selectedCoursesView = new SelectedView({
                el: $('#selected_courses'),
                semester: this.semester
            });
        }
    },
    swapView: function(newView, name){
        if(this.viewType == name)
            return;
        if(this.subview){
            this.subview.destroy();
        }
        this.subview = newView.render();
        this.viewType = name;
    },
    showDepartments: function(){
        this.swapView(new DepartmentsView({
            el: $('#departments'),
            semester: this.semester
        }), 'departments');
    },
    showCourses: function(){
        this.swapView(new CoursesView({
            el: $('#courses'),
            semester: this.semester
        }), 'courses');
    },
    showSelected: function(){
        this.swapView(new SelectedView({
            el: $('#selected'),
            semester: this.semester
        }), 'selected');
    },
    showSchedules: function(){
        this.swapView(new SchedulesView({
            el: $('#schedules'),
            semester: this.semester
        }), 'schedules');
    },
    autodetectActiveView: function(){
        function exists(el){ return $(el).length; }
        if(exists('#department'))
            return this.showDepartments();
        if(exists('#schedules'))
            return this.showSchedules();
        if(exists('#selected'))
            return this.showSelected();
    }
});

var Workspace = Backbone.Router.extend({
   routes: {
        'selected':                 'selected',
        '':                         'catalog',
        'search/':                  'search',
        'search/?q=:query':         'search',
        'search/?q=:query&d=:dept': 'search',
        'schedules':                'schedules'
   },

   selected: function(){

   },
   search: function(){

   },
   schedules: function(){

   }
});

$(function(){
    /* Until done
    new Workspace();
    Backbone.history.start({pushState: true, silent: true});
    */
    window.app = new AppView(2011, 9);
});

})(document, window, jQuery, Backbone, _);
