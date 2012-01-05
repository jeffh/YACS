(function(Backbone, _, window, undefined){

  function readOnlySync(method, model, options){
    if (_.include(['create', 'update', 'delete'], method))
      return;
    return Backbone.sync(method, model, options);
  }

  function api(){
    return '/api/v3/' + Array.prototype.join.call(arguments, '/') + '/';
  }
  function parseJSONReponse(json){
    if (json.status === 'OK'){
      return json.payload;
    } else {
      console.log('JSON request failed: ', json);
    }
  }

  var ModelBase = Backbone.Model.extend({
    initialize: function(attributes){
      var self = this;
      _.each(attributes, function(value, name){
        var klass = window[(self.collectionFields || {})[name]];
        if (klass){
          obj = {};
          obj[name] = self._collectionize(value, klass);
          self.set(obj, {slient: true});
        }
      });
    },
    _collectionize: function(json, collectionClass){
      var collection = new collectionClass();
      _.each(json, function(item){
        collection.create(item);
      });
      return collection;
    },
    collectionFields: null,
    sync: readOnlySync,
    jsonifyFields: [],
    toJSON: function(){
      var data = Backbone.Model.prototype.toJSON.call(this);
      data.url = this.url().substr('/api/v3'.length);
      var self = this;
      _.each(this.jsonifyFields || [], function(name){
        data[name] = self.get(name).toJSON();
      });
      return data;
    },
    parse: parseJSONReponse
  });

  var CollectionBase = Backbone.Collection.extend({
    semesterID: null,
    getSemesterQueryString: function(){
      if (!this.get('semesterID')){
        return '';
      }
      return 'semester=' + this.get('semesterID');
    },
    parse: parseJSONReponse
  });

  var Semester = ModelBase.extend({
    url: function(){
      return api('semesters', this.id);
    }
  });

  var Department = ModelBase.extend({
    url: function(){
      var sem = this.get('semester');
      return api('departments', this.get('code'));
    }
  });

  var Course = ModelBase.extend({
    defaults: {
      marked: false,
      sections: null
    },
    url: function(){
      var sem = this.get('semester');
      return api('courses', this.id);
    },
    jsonifyFields: ['semester'],
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

  var Section = ModelBase.extend({
    defaults: {
      marked: false
    },
    idAttribute: 'crn',
    collectionFields: {periods: 'PeriodList'},
    jsonifyFields: ['course', 'semester'],
    url: function(){
      var sem = this.get('semester');
      return api('sections', this.get('crn'));
    },
    mark: function(){
      this.set({marked: true});
      console.log('section marked ' + this.get('crn'));
    },
    unmark: function(){
      this.set({marked: false});
      console.log('section unmarked ' + this.get('crn'));
    }
  });

  var Period = ModelBase.extend({
    url: function(){
      return api('periods', this.id);
    }
  });

  var Semesters = ModelBase.extend({
    model: Semester,
    comparator: function(semester){
      return semester.get('year') * 12 + semester.get('month');
    },
    url: function(){
      return api('semesters');
    }
  });
  var Departments = CollectionBase.extend({
    model: Department,
    url: function(){
      return api('departments') + '?' + this.getSemesterQueryString();
    }
  });
  var Courses = CollectionBase.extend({
    model: Course,
    url: function(){
      return api('courses') + '?' + this.getSemesterQueryString();
    }
  });
  var Sections = CollectionBase.extend({
    model: Section,
    url: function(){
      return api('sections') + '?' + this.getSemesterQueryString();
    }
  });
  var Periods = CollectionBase.extend({
    model: Period,
    url: function(){
      return api('periods') + '?' + this.getSemesterQueryString();
    }
  });

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

})(Backbone, _, window);
