(function(document, window, $, Backbone, _, undefined){

var Semester = Backbone.Model.extend({
    defaults: {
        year: 2011,
        month: 9,
        last_updated: null
    }
});

var Selection = Backbone.Model.extend({
    defaults: {
        courses: null // course_id => [crns]
    }
});

var ListView = Backbone.Model.extend({
    defaults: {
        items: null
    }
});


})(document, window, jQuery, Backbone, _);
