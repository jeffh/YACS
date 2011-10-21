(function($, window, document, undefined){

var original_page_content = null;
var request = null;
var fuse = new Utils.Fuse({
    delay: 200,
    execute: function(){
        if(request)
            request.abort();

        var dept = $('#d').val(),
            query = $('#q').val(),
            url = $('#searchform').attr('action') + '?partial=1&' + $.param({d: dept, q: query}),
            target = $('#replacable-with-search');

        if(dept === 'all' && $.trim(query) === ''){
            target.html(original_page_content);
            return;
        }

        console.log('performing search: ' + url);

        request = $.ajax(url, {
            type: 'get',
            dataType: 'text',
            complete: function(){
                request = null;
            },
            success: function(content, status, request){
                target.html(content);
                $('.actions', target).hide();
                console.log('Got Results');
            },
            error: function(request, status, error){
                if(status === 'abort'){
                    console.log('Aborted');
                    return;
                }
                target.html(original_page_content);
                console.log('Search Request Failed: ' + status + '; ' + error);
            }
        });
    }
});

function performSearch(){
    if(!$('#replacable-with-search').length){
        console.log('#replacable-with-search not found');
        return; // we don't know what content we can destroy. ARGGH!!
    }
    fuse.stop();
    fuse.start();
}

$(function(){
    original_page_content = $('#replacable-with-search').html();
    $('#d').bind('change', performSearch);
    $('#q').bind('search', performSearch).bind('keyup', performSearch);
});

})(jQuery, window, document);
