// require: objects.js

///////////////////////////////////////////////////
// Hooks

// realtime search initialization
$(function(){
	var defaultHtml = $('#replacable-with-search').html();
	var searchElement = $('#searchform');
	if(searchElement.length){
		var SearchForm = new RealtimeForm(searchElement, {
            cache: true,
			updateElement: '#replacable-with-search',
			additionalGET: {partial: 1},
            activityResponder: new ActivityResponder({
              show: function(){
                $('#search-spinner').show();
              },
              hide: function(){
                $('#search-spinner').hide();
              }
            }),
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

Scheduler = {};
Scheduler.selection = new Selection();

//  Selected Course Feature
$(function(){
  $('#courses .course > input[type=checkbox], #courses .course .section > input[type=checkbox]').bind('change', function(){
    //(this.checked ? selected.add : selected.remove)(this);
    console.log(this.checked);
    (this.checked ? Scheduler.selection.add(this) : Scheduler.selection.remove(this));
  });
  // automatically refresh after any changes
  var refresh = function(){
    Scheduler.selection.refresh();
  };
  $(Scheduler.selection).bind('added', refresh).bind('removed', refresh);
});
