(function(Backbone, _, undefined){

function api(){
    return '/api/' + Array.prototype.join.call(arguments, '/') + '/';
}
function includeURLinToJSON(){
    var data = Backbone.Model.prototype.toJSON.call(this);
    data.url = this.url().substr('/api'.length);
    var self = this;
    _.each(this.jsonifyFields || [], function(name){
        data[name] = self.get(name).toJSON();
    });
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
    defaults: {
        marked: false,
        sections: null
    },
    url: function(){
        var sem = this.get('semester');
        return api(sem.get('year'), sem.get('month'), this.get('code'), this.get('number'));
    },
    jsonifyFields: ['semester'],
    toJSON: includeURLinToJSON,
    mark: function(){
        _.each(this.get('sections'), function(section){
            section.mark();
        });
        this.set({marked: true});
        console.log('course marked ' + this.get('name'));
    },
    unmark: function(){
        _.each(this.get('sections'), function(section){
            section.unmark();
        });
        this.set({marked: false});
        console.log('course unmarked ' + this.get('name'));
    }
});

var Section = Backbone.Model.extend({
    defaults: {
        marked: false
    },
    jsonifyFields: ['course', 'semester'],
    url: function(){
        var sem = this.get('semester');
        return api(sem.get('year'), sem.get('month'), this.get('code'), this.get('number'), 'crn-' + this.get('crn'));
    },
    toJSON: includeURLinToJSON,
    mark: function(){
        this.set({marked: true});
        console.log('section marked ' + this.get('crn'));
    },
    unmark: function(){
        this.set({marked: false});
        console.log('section unmarked ' + this.get('crn'));
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
var Departments = Backbone.Collection.extend({ model: Department });
var Courses = Backbone.Collection.extend({ model: Course });
var Sections = Backbone.Collection.extend({ model: Section });
var Periods = Backbone.Collection.extend({ model: Period });

// export
_.extend(window, {
    Semester: Semester,
    Department: Department,
    Course: Course,
    Section: Section,
    Period: Period,
    SemesterList: Semesters,
    DepartmentList: Departments,
    CourseList: Courses,
    SectionList: Sections,
    PeriodList: Periods
})

})(Backbone, _);
