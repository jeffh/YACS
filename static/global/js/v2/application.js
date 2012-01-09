// require: objects.js

///////////////////////////////////////////////////
// Hooks

// realtime search initialization
$(function(){
	var defaultHtml = $('#replacable-with-search').html();
	var searchElement = $('#searchform');
	if(searchElement.length){
		var SearchForm = new RealtimeForm(searchElement, {
			updateElement: '#replacable-with-search',
			additionalGET: {partial: 1},
			activityIndicatorElement: '#search-spinner',
			suppressFormSubmit: true,
			customHandler: function(form, fuse){
				var dept = form.find('#d').val(),
					query = form.find('#q').val();
				if(query === '' && dept === 'all'){
					$('#replacable-with-search').html(defaultHtml);
					return true;
				}
				fuse.start();
				return false;
			}
		});
	}
});

//  Selected Course Feature
var selected;
$(function(){
  selected = new Selected();
  $('#courses .course > input[type=checkbox], #courses .course .section > input[type=checkbox]').bind('change', function(){
    //(this.checked ? selected.add : selected.remove)(this);
    (this.checked ? selected.add(this) : selected.remove(this));
  });
  // automatically refresh after any changes
  var refresh = selected.refresh.bind(selected);
  $(selected).bind('added', refresh).bind('removed', refresh);
});
