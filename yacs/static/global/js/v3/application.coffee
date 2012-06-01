YACS =
    summary_length: 150
    search_delay: 1000

# summarize course descriptions
$(-> summarize($('.summarize'), {summary_length: YACS.summary_length}))

# realtime search
$(->
    spinner = $('#search-spinner')
    target = $('#replacable-with-search')
    realtime_form('#searchform', target, {
        delay: YACS.search_delay
        serializer: (form, method) -> form.serialize() + '&partial=1'
        event_start: -> spinner.show()
        request_start: -> Logger.info('search query: ' + $('#q').val())
        complete: -> spinner.fadeOut(500)
        success: ->
            summarize(
                target.find('.summarize'),
                {summary_length: YACS.summary_length})
    })
)

# hooks to selection
$(->
    window.selection = selection = new Selection()
    $('.course > input[type=checkbox], .section > input[type=checkbox]').live('change', ->
        cid = parseInt($(this).attr('data-cid'), 10)
        crn = parseInt($(this).attr('data-crn'), 10)
        if crn?
            selection.toggle_section(cid, crn)
        else
            crns = [parseInt(x, 10) for x in $(this).attr('data-crns').split(', ')]
            full_crns = [parseInt(x, 10) for x in $(this).attr('data-crns-full').split(', ')]
            free_crns = set_difference(crns, full_crns)
            selection.toggle_course(cid, free_crns)
            # TODO: check all sections behavior
    )
)
