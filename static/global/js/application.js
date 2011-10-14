(function(document, window, $, Backbone, _, undefined){

function api(){
    return '/api/' + Array.prototype.join.call(arguments, '/') + '/';
}
function includeURLinToJSON(){
    var data = Backbone.Model.prototype.toJSON.call(this);
    data.url = this.url().substr('/api'.length);
    return data;
}

var Semester = Backbone.Model.extend({
    url: function(){
        return api(this.get('year'), this.get('month'));
    },
    toJSON: includeURLinToJSON
});

var Department = Backbone.Model.extend({
    url: function(){
        var sem = this.get('semester');
        return api(sem.get('year'), sem.get('month'), this.get('code'));
    },
    toJSON: includeURLinToJSON
});

var Course = Backbone.Model.extend({
    url: function(){
        var sem = this.get('semester');
        return api(sem.get('year'), sem.get('month'), this.get('code'), this.get('number'));
    },
    toJSON: includeURLinToJSON
});

var Section = Backbone.Model.extend({
    defaults: {
        marked: false
    },
    url: function(){
        var sem = this.get('semester');
        return api(sem.get('year'), sem.get('month'), this.get('code'), this.get('number'), 'crn-' + this.get('crn'));
    },
    toJSON: includeURLinToJSON,
    mark: function(){
        this.set('marked', true);
    },
    unmark: function(){
        this.set('marked', false);
    }
});

var Period = Backbone.Model.extend({
    url: function(){
        var semester = this.section.semester;
        return api('periods', this.id);
    },
    toJSON: includeURLinToJSON
});

var Semesters = Backbone.Collection.extend({
    model: Semester,
    comparator: function(semester){
        return semester.get('year') * 12 + semester.get('month');
    },
    toJSON: includeURLinToJSON
});
var DepartmentList = Backbone.Collection.extend({ model: Department });
var CourseList = Backbone.Collection.extend({ model: Course });
var SectionList = Backbone.Collection.extend({ model: Section });
var PeriodList = Backbone.Collection.extend({ model: Period });

var ItemView = Backbone.View.extend({
    tagName: 'li',
    template: null,

    initialize: function(){
        this.model.bind('change', this.render, this);
        this.model.bind('destroy', this.remove, this);
        this.template = this.options.template;
        this.subview = null;
    },
    render: function(){
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

    checkbox: function(){
        return this.$('input[type=checkbox]:first');
    },

    mark: function(){
        this.checkbox().attr('checked', 'checked');
        this.model.mark();
    },
    unmark: function(){
        this.checkbox().removeAttr('checked');
        this.model.unmark();
    },
    toggleMark: function(){
        if (this.checkbox().attr('checked'))
            unmark();
        else
            mark();
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
            console.log("department: " + code + ', ' + name);
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
    ItemView: MarkableItemView,

    initialize: function(){
        this.semester = this.options.semester;
        this.ItemView = this.options.ItemView || this.ItemView;
        this.courses = this.options.courseList || new CourseList();
        this.sections = this.options.sectionList || new SectionList();
        this.mapping = {}; // course.id => section.crn

        this.courses.bind('all', this.render, this);
        this.sections.bind('all', this.render, this);
    },
    add: function(course, sections){
        this.courses.add(course);
        this.sections.add(section);
        this.mapping[course.id] = this.mapping[course.id] || [];
        _.each(sections, function(section){
            this.mapping[course.id].push(section.crn);
        }, this);

        var course_template = $('#selected-course-template').html(),
            section_template = $('#selected-section-template').html();
        var course_view = new this.ItemView({
            model: course,
            template: course_template
        });
        var section_view = new this.ItemView({
            model: section
        });
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
        this.selectedCoursesView = new SelectedView({
            el: $('#selected_courses'),
            semester: this.semester
        });
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
