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

# synchronizes the UI checkboxes to the given selection instance
sync_selection = (selection) ->
    $('.course > input[type=checkbox], .section > input[type=checkbox]').checked(false)
    for cid in selection.course_ids()
        $('#course_' + cid).checked(true)
        Logger.info('check', '#course_' + cid)
        for section_id in selection.get(cid)
            $('#section_' + section_id).checked(true)
            Logger.info('check', '#section_' + section_id)
    Logger.info("Synced UI with selection.")

# hooks to selection
$(->
    window.conflictor = ConflictDetector()
    api.conflicts(((data) ->
        Logger.info('Loaded conflict data.')
        conflictor.update(data)),
        -> Logger.error('Failed to load conflicts'))
    window.selection = selection = new Selection(
        conflictor: conflictor
    )
    $('.course > input[type=checkbox], .section > input[type=checkbox]').live('change', ->
        cid = parseInt($(this).attr('data-cid'), 10)
        sid = $(this).attr('data-sid')
        if sid?
            Logger.info("section#" + sid + " toggled")
            course_is_empty = selection.toggle_section(cid, parseInt(sid, 10))
            # if the course checkbox isn't checked, check that.
            # Likewise in reverse, if no sections are checked, uncheck course.
            $('#course_' + cid).checked(!course_is_empty)
        else
            sids = array_of_ints($(this).attr('data-sids'))
            full_sids = array_of_ints($(this).attr('data-sids-full'))
            free_sids = _.difference(sids, full_sids)
            is_checked = selection.toggle_course(cid, free_sids)
            # check all sections behavior; needs to do:
            # - check all free sections if course is checked
            # - uncheck all checkboxes if a section is already checked
            # - check all sections if there are no free sections
            if is_checked
                if free_sids.length
                    Logger.info("Course#" + cid + " toggled - checked free: " + free_sids.join(', '))
                    for id in free_sids
                        $('#section_' + id).checked(true)
                else
                    Logger.info("Course#" + cid + " toggled - checked all")
                    for id in sids
                        $('#section_' + id).checked(true)
            else
                Logger.info("Course#" + cid + " toggled - unchecked")
                $('#course_' + cid).parent().find('.section input[type=checkbox]').checked(false)
    )
    sync_selection(selection)
)
