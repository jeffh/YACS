# stop attaching hooks if we're in jasmine tests
return if $('.content').length == 0

days_of_the_week = 'Monday Tuesday Wednesday Thursday Friday'.split(' ')

create_summaries = ->
    elements = $('.summarize').not('.has-summary')
    summarize(elements, summary_length: 150)
    elements.addClass('has-summary')

# summarizer
$ -> create_summaries()

templates = null
$ -> window.templates = templates = find_templates()

# search form
$ ->
    spinner = $('#search-spinner')
    original_html = $('#replacable-with-search').html()
    updateform('#searchform',
        start: -> spinner.show()
        data: {partial: 1}
        update: (html) ->
            $('#replacable-with-search').html(html)
            create_summaries()
            visualize_conflicts()
            spinner.fadeOut()
        empty: ->
            $('#replacable-with-search').html(original_html)
            visualize_conflicts()
        error: -> spinner.fadeOut()
    )

$ ->
    # set API to filter by semester_id
    data = $('meta[name=semester_id]')
    if data.length
        api.filter(semester_id: parseInt(data.attr('content'), 10))

# initialize selection validation system
courses = null
window.validator = validator = new Validator()
has_initialized = false
initialize_validator = ->
    return if has_initialized
    $('input[type=checkbox]').attr('disabled', 'disabled')
    callback = barrier(3, ->
        has_initialized = true
        $('input[type=checkbox]').removeAttr('disabled')
        $(validator).trigger('load')
    )
    api.courses((data) ->
        courses = data
        callback()
    )
    api.conflicts((conflicts) ->
        validator.set_conflicts(conflicts)
        callback()
    )
    api.sections((sections) ->
        validator.set_sections(sections)
        callback()
    )
initialize_validator()

# initialize selection modification
conflict_runner = null
visualize_conflicts = () ->
    if conflict_runner?
        conflict_runner.abort()
    conflict_runner = iterate($('.course > input[type=checkbox]'), {
        each: (element, i) ->
            el = $(element)
            course_id = parseInt(el.attr('data-cid'), 10)
            section_ids = array_of_ints(el.attr('data-sids'))
            s = selection.copy()
            validator.set_data(s.data)
            conflicted_sections = []
            sec2course = {} # track course ids
            for section_id in section_ids
                # slower check of conflicts (more accurate)
                s.add_section(course_id, section_id)
                validator.set_data(s.data)
                unless validator.is_valid()
                    conflicted_sections.push(section_id)
                    sec2course[section_id] = course_id
                s.undo()

            course = $('#course_' + course_id).parent().removeClass('conflict')
            course.find('.conflict').removeClass('conflict')
            course.find('.conflicts_with_course, .conflicts_with_section').remove()
            course.find('input[type=checkbox]').removeAttr('disabled')

            # full-course conflict
            conflicted_sections = _.uniq(conflicted_sections)
            if conflicted_sections.length == section_ids.length
                return if $('#course_' + course_id).checked()
                course.addClass('conflict')
                if sec2course[conflicted_sections[0]]?
                    name = courses.get(sec2course[conflicted_sections[0]]).get('name')
                else
                    name = 'selection'
                course.append(templates.conflict_template(
                    classname: 'conflicts_with_course'
                    name: name
                ))
                course.find('input[type=checkbox]').attr('disabled', 'disabled')
            else # per section conflict
                for section_id in conflicted_sections
                    continue if $('#section_' + section_id).checked()
                    section = $('#section_' + section_id).attr('disabled', 'disabled')
                    section = section.parent().addClass('conflict')
                    if sec2course[conflicted_sections[0]]?
                        name = courses.get(sec2course[section_id]).get('name')
                    else
                        name = 'selection'
                    section.find('label').append(templates.conflict_template(
                        classname: 'conflicts_with_section'
                        name: name
                    ))
        end: -> conflict_runner = null
    })

# visualize conflicts after selection has been applied
$(validator).bind('load', ->
    visualize_conflicts()
)

# course selection system
window.selection = selection = new Selection().load()
$ ->
    for cid in selection.get_courses()
        $('#course_' + cid).checked(true)
        for sid in selection.get(cid)
            $('#section_' + sid).checked(true)

# checkboxes for storage
$ ->
    $('.course > input[type=checkbox]').live 'click', ->
        el = $(this)
        is_checked = el.checked()
        course_id = parseInt(el.attr('data-cid'), 10)
        section_ids = array_of_ints(el.attr('data-sids'))
        full_section_ids = array_of_ints(el.attr('data-sids-full'))
        free_section_ids = _.difference(section_ids, full_section_ids)

        parent = el.parent()
        sections = (if free_section_ids.length then free_section_ids else section_ids)

        if is_checked
            valid_sections = []
            for section_id in sections
                validator.set_data(selection.data)
                selection.add_section(course_id, section_id)
                validator.set_data(selection.data)
                if not validator.is_valid(section_ids)
                    console.log('undo', section_id)
                    selection.undo() # reverse!
                else
                    console.log('add', section_id)
                    valid_sections.push(section_id)

            for section_id in valid_sections
                parent.find('#section_' + section_id).checked(is_checked)

            if valid_sections.length == 0
                el.checked(false)
                return false
        else
            validator.set_data(selection.data)
            selection.remove_course(course_id, section_ids)
            for section_id in sections
                parent.find('#section_' + section_id).checked(is_checked)

        visualize_conflicts()
        selection.save()

    $('.section > input[type=checkbox]').live 'click', ->
        el = $(this)
        is_checked = el.checked()
        course_id = parseInt(el.attr('data-cid'), 10)
        section_id = parseInt(el.attr('data-sid'), 10)

        validator.set_data(selection.data)
        if validator.conflicts_with(section_id)
            return false

        if is_checked
            selection.add_section(course_id, section_id)
        else
            selection.remove_section(course_id, section_id)
        validator.set_data(selection.data)

        if not validator.is_valid()
            selection.undo()
            return false

        parent = el.parents('.course')
        checked_courses = false
        parent.find('.section > input[type=checkbox]').each ->
            if $(this).checked() == true
                checked_courses = true

        if not checked_courses or is_checked
            parent.find('> input[type=checkbox]').checked(is_checked)

        visualize_conflicts()
        selection.save()

template_functions = {
    display_time: (period) ->
        fmt = '{{ 0 }}-{{ 1 }}'
        start = Time.parse_military(period.start)
        end = Time.parse_military(period.end)
        time_fmt = '{{ hour }}{{ sep_if_min }}{{ zmin_if_min }}'
        format(fmt,
            start.format(time_fmt + (if (start.isAM() == end.isAM()) or (start.isPM() == end.isPM()) then '' else '{{ apm }}')),
                            end.format(time_fmt + '{{ apm }}')
        )
    periods_by_dow: (periods) ->
        remapped_periods = {}
        for dow in days_of_the_week
            remapped_periods[dow] = []
        for period in periods
            for dow in period.days_of_the_week
                remapped_periods[dow].push(period)
        remapped_periods
    pluralize: (text, number, pluralize_text) ->
        pluralize_text ?= 's'
        if number != 1
            text + pluralize_text
        else
            text
    period_offset: (period, height) ->
        start = Time.parse_military(period.start)
        time = start.minute * 60 + start.second
        return time / 3600.0 * height
    period_height: (period, height) ->
        time = Time.parse_military(period.end).toInt() - Time.parse_military(period.start).toInt()
        #return 25 // 30 min time block
        #return 41.666666667 // 50 min time block
        return time / 3600.0 * height
}

saved_selection_id = ->
    path = location.href.split('/')
    index = path.indexOf('selected')
    if index == -1 || path.length - 1 == index
        return 0
    parseInt(path[index + 1], 10)

# selected courses
$ ->
    target = $('#selected_courses')
    return unless target.length

    process_selection = ->
        saved_id = saved_selection_id()
        $('[data-action=clear-selection]').hide() if saved_id
        if saved_id
            api.selection(
                ((sel) ->
                    window.selection = selection = new Selection(data: sel.get('data'), read_only: true)
                    display_selection()
                ),
                (-> console.error('Failed to load selection')),
                saved_id
            )
        else
            display_selection()

    display_selection = ->
        $('[data-action=clear-selection]').click ->
            if confirm('Clear all your selected courses?')
                selection.clear()
                location.reload()
            return false

        if selection.has_courses()
            sections = null
            departments = null
            courses = null
            callback = barrier(3, ->
                target.empty()
                for course_id in selection.get_courses()
                    course = courses.get(course_id).to_hash()
                    course.sections = (->
                        results = _.filter(sections.to_array(), (s) -> s.get('course_id') == course.id)
                        _.map(results, (s) -> s.to_hash())
                    )()
                    for section in course.sections
                        section.instructors = (->
                            _.pluck(section.section_times, 'instructor')
                        )()
                        section.seats_left = section.seats_total - section.seats_taken
                    course.section_ids = (->
                        _.pluck(course.sections, 'id')
                    )()
                    course.full_section_ids = (->
                        _.pluck(_.filter(course.sections, (s) ->
                            s.seats_taken >= s.seats_total
                        ), 'id')
                    )()
                    course.seats_total = (->
                        _.reduce(course.sections,
                            ((accum, item) -> accum + item.seats_total),
                            0
                        )
                    )()
                    course.seats_taken = (->
                        _.reduce(course.sections,
                            ((accum, item) -> accum + item.seats_left),
                            0
                        )
                    )()
                    course.seats_left = course.seats_total - course.seats_left
                    course.department = (->
                        departments.get(course.department_id).to_hash()
                    )()
                    course.instructors = (->
                        kinds = []
                        for section in course.sections
                            for times in section.section_times
                                pushUnique(kinds, times.instructor)
                        kinds
                    )()
                    course.kinds = (->
                        kinds = []
                        for section in course.sections
                            for times in section.section_times
                                pushUnique(kinds, times.kind)
                        kinds
                    )()
                    course.notes = (->
                        _.pluck(course.sections, 'notes')
                    )()

                    target.append(templates.course_template(
                        course: course
                        days_of_the_week: days_of_the_week
                        _: _
                        alwaysShowSections: true
                        isReadOnly: false
                        isSelectedSection: (section_id) -> _.include(selection.get_sections(), section_id)
                        displayTime: template_functions.display_time
                        periodsByDayOfWeek: template_functions.periods_by_dow
                        pluralize: template_functions.pluralize
                    ))
                create_summaries('.summarize')
            )
            api.courses (data) ->
                courses = data
                callback()
            api.sections (data) ->
                sections = data
                callback()
            api.departments (data) ->
                departments = data
                callback()
        else
            target.html(templates.no_courses_template())

    process_selection()

# cycles numbers based on the number of schedule items
create_color_map = (schedule, maxcolors) ->
    color_map = {}
    maxcolors = maxcolors or 9
    keys = Object.keys(schedule)
    for i in [0..keys.length]
        cid = keys[i]
        color_map[cid] = (i % maxcolors) + 1
    return color_map

# creates a nested object for easily accessing sections by time slot:
# map[day_of_the_week][starting_hour] = section
create_timemap = (schedule, sections, dows, time_range) ->
    map = {}
    for dow in dows
        map[dow] = {}
    scheduleSections = []

    section_ids = (schedule[cid] for cid in Object.keys(schedule))

    for section_id in section_ids
        scheduleSections.push(sections.get(section_id).to_hash())

    for section in scheduleSections
        for period in section.section_times
            for dow in period.days_of_the_week
                startingHour = Time.parse_military(period.start).hour
                map[dow][startingHour] = period
    map


# used to change the UI appropriately when a section changes
create_set_index_for_schedule = (schedules, response, courses, sections, departments, dows, time_range, color_map) ->
    # use lock-like mechanism to prevent recursive calls because of re-trigging History state change
    ignoreStateChange = false
    return (index, options) ->
        options = $.extend({
            replace: false
        }, options)
        if index >= schedules.length or index < 0 or ignoreStateChange
            return
        ignoreStateChange = true
        schedule = schedules[index]
        timemap = create_timemap(schedule, sections, dows, time_range)
        secs = []

        for section_id in schedule
            secs.push(sections.get(section_id).to_hash())

        current_schedule.selected_index = index
        state = {
            offset: index + 1
            schedule: response.result.id
        }
        new_url = format('{{ base }}{{ id }}/{{ offset }}/',
            base: $('#schedules').attr('data-url-base')
            id: state.schedule
            offset: state.offset
        )
        if options.replace
            History.replaceState(state, null, new_url)
        else
            History.pushState(state, null, new_url)

        $('.thumbnail').removeClass('selected')
        $($('.thumbnail')[index]).addClass('selected')
        height = parseInt($('#schedule_template').attr('data-period-height'), 10)
        $('#schedules').html(templates.schedule_template(
            sid: index + 1 #response.result.id
            schedules: schedules
            dows: response.result.days_of_the_week
            timemap: timemap
            time_range: response.result.time_range
            color_map: color_map
            courses: courses
            sections: sections
            departments: departments
            crns: _.map(_.values(schedules[index]), (sid) -> sections.get(sid).get('crn'))
            displayTime: template_functions.display_time
            pluralize: template_functions.pluralize
            period_height: (p) -> template_functions.period_height(p, height)
            period_offset: (p) -> template_functions.period_offset(p, height)
            humanize_hour: (h) ->
                new Time(h, 0, 0).format('{{ hour }} {{ apm }}')
            humanize_time: (time) ->
                time = Time.parse_military(time)
                time.format('{{ hour }}')
        ))
        ignoreStateChange = false

current_schedule = {}
display_schedules = (options) ->
    options = $.extend({
        selected_index: 0
        section_ids: null
        id: null
    }, current_schedule, options)
    current_schedule = options
    target = $('#thumbnails')
    callback = barrier(4, ->
        unless @response.success
            Logger.error(@response)
            return

        current_schedule.id = @response.result.id
        schedules = @response.result.schedules
        dows = @response.result.days_of_the_week
        time_range = @response.result.time_range

        if schedules.length
            color_map = create_color_map(schedules[0], 8)
            thumbnails_html = []
            for i in [0..schedules.length - 1]
                schedule = schedules[i]
                timemap = create_timemap(schedule, @sections, dows, time_range)
                secs = []

                for section_id in schedule
                    secs.push(@sections.get(section_id).to_hash())

                height = parseInt($('#thumbnail_template').attr('data-period-height'), 10)
                # render thumbnail
                thumbnails_html.push(templates.thumbnail_template(
                    sid: i + 1
                    schedules: schedules
                    dows: @response.result.days_of_the_week
                    timemap: timemap
                    time_range: @response.result.time_range
                    color_map: color_map
                    courses: @courses
                    sections: @sections
                    period_height: (p) -> template_functions.period_height(p, height)
                    period_offset: (p) -> template_functions.period_offset(p, height)
                ))
            # render selected template
            current_schedule.set_selected_index = create_set_index_for_schedule(schedules, @response, @courses, @sections, @departments, dows, time_range, color_map)
            current_schedule.set_selected_index(options.selected_index, {replace: true})
            target.html(thumbnails_html.join(''))
            bind_schedule_events()
            $('#schedule_thumbnail' + (options.selected_index + 1)).addClass('selected')
        else
            $('#schedules').html(templates.no_schedules_template())
        if schedules.length < 2
            target.hide()
    )

    api.courses((data) ->
        callback(-> @courses = data)
    )
    api.sections((data) ->
        callback(-> @sections = data)
    )
    api.departments((data) ->
        callback(-> @departments = data)
    )
    api.schedules(
        section_ids: options.section_ids
        id: options.id
        success: (r) ->
            callback(-> @response = r)
    )

bind_schedule_events = ->
    hide_schedules = ->
        $('#thumbnails').hide(200)
        return false

    $('.view-schedules').live('click', ->
        $('#thumbnails').toggle(200)
        return false
    )
    $('#thumbnails .select-schedule').live('click', ->
        schedule_id = parseInt($(this).parent().attr('data-sid'), 10) - 1
        current_schedule.set_selected_index(schedule_id)
        hide_schedules()
        return false
    )
    KEY = {
        LEFT: 37
        RIGHT: 39
    }
    # bind keyboard shortcuts
    $(window).bind('keyup', (e) ->
        index = current_schedule.selected_index
        if e.keyCode == KEY.LEFT
            current_schedule.set_selected_index(index - 1)
        else if e.keyCode == KEY.RIGHT
            current_schedule.set_selected_index(index + 1)
    )
    window.current_schedule = current_schedule

# schedules view
$ ->
    target = $('#thumbnails')
    return unless target.length

    # requires browser support
    if History.enabled
        state_changed = ->
            state = History.getState()
            if state.id
                current_schedule.set_selected_index(state.data.offset - 1)
        History.Adapter.bind(window, 'statechange', state_changed)
        History.Adapter.bind(window, 'hashchange', state_changed)

    state = History.getState()
    if state.data.schedule
        index = state.data.offset or parseInt($('#schedules').attr('data-start'), 10) or 0
        schedule_id = state.data.schedule or $('#schedules').attr('data-schedule')
    else
        index = parseInt($('#schedules').attr('data-start'), 10) or 0
        schedule_id = $('#schedules').attr('data-schedule')
    if schedule_id == ''
        schedule_id = null
    display_schedules
        id: schedule_id
        section_ids: selection.get_sections()
        selected_index: Math.max(index - 1, 0)

    # update selection url
    api.schedules
        id: schedule_id
        section_ids: selection.get_sections()
        success: (data) ->
            current_sids = data.result.section_ids
            is_equal = _.difference(current_sids, selection.get_sections()).length == 0

            if not is_equal
                $el = $('.selected_courses.button')
                href = $el.attr('href')
                if href.indexOf('/selected/') == href.length - '/selected/'.length
                    $el.attr('href', href + data.result.id+ '/')
