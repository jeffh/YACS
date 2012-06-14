YACS =
    summary_length: 150
    search_delay: 1000

window.templates = {_processed: 0}

$(-> window.templates = find_templates())

# summarize course descriptions
create_summaries = -> summarize($('.summarize'), summary_length: YACS.summary_length)
$(create_summaries)

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

# selection courses display
$(->
    target = $('#selected_courses')
    if not target.length
        return
    #templates.course_template()
    if selection.is_empty()
        target.html(templates.no_courses_template())
    else
        target.empty()
        window.api.courses(((courses) ->
            context =
                alwaysShowSections: true
                days_of_the_week: 'Monday Tuesday Wednesday Thursday Friday'.split(' ')
                periodsByDayOfWeek: (periods) ->
                    remapped_periods = {}
                    self.options.dows.each((dow) ->
                        remapped_periods[dow] = []
                    )
                    for period in periods
                        period.get('days_of_the_week').each((dow) ->
                            remapped_periods[dow].push(period)
                        )
                    return remapped_periods
                isSelectedCRN: (sid) -> selection.has_section_id(sid)
                requires_truncation: (string, max) -> !string or string.length > max
                truncate: (string, max) ->
                    if (string.substring(0, max) == string)
                        return string
                    return string.substring(0, max - 3) + '...'
                bold_topics_include: (string) ->
                    string.replace('Topics include', '<strong>Topics include</strong>')
                displayPeriod: (p) ->
                    fmt = '{{ 0 }}-{{ 1 }}'
                    start = FunctionsContext.time_parts(p.get('start'))
                    end = FunctionsContext.time_parts(p.get('end'))
                    return format(fmt,
                        FunctionsContext.humanize_time(p.get('start'), {includesAPM: false})
                        FunctionsContext.humanize_time(p.get('end'))
                    )
                isReadOnly: true
            for cid in selection.course_ids()
                context.course = courses.get(cid)
                Logger.info(context.course)
                target.append(templates.course_template(context))
            create_summaries()
        ), -> Logger.error('Failed to fetch courses'))
)
