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
    updateform('#searchform',
        start: -> spinner.show()
        update: (html) ->
            $('#replacable-with-search').html(html)
            create_summaries()
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
            conflicted_sections = []
            s = selection.copy()
            validator.set_data(s.data)
            sec2course = {} # track course ids
            for section_id in section_ids
                cid = validator.conflicts_with(section_id)
                if cid?
                    conflicted_sections.push(section_id)
                    sec2course[section_id] = cid
                else
                    s.add_section(course_id, section_id)
                    validator.set_data(s.data)
                    unless validator.is_valid()
                        conflicted_sections.push(section_id)
                    s.undo()

            course = $('#course_' + course_id).parent().removeClass('conflict')
            course.find('.conflict').removeClass('conflict')
            course.find('.conflicts_with_course, .conflicts_with_section').remove()
            course.find('input[type=checkbox]').removeAttr('disabled')

            # full-course conflict
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
    if selection.has_courses()
        initialize_validator()
    else if $('input[type=checkbox]').length
        initialize_validator()

    that = this
    $('.course > input[type=checkbox]').click ->
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
                unless validator.conflicts_with(section_id)
                    selection.add_section(course_id, section_id)
                    validator.set_data(selection.data)
                    if not validator.is_valid(section_ids)
                        console.log('undo', section_id)
                        selection.undo() # reverse!
                    else
                        console.log('add', section_id)
                        valid_sections.push(section_id)
                else
                    console.log('obvious conflict', section_id)

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

    $('.section > input[type=checkbox]').click ->
        el = $(this)
        is_checked = el.checked()
        course_id = parseInt(el.attr('data-cid'), 10)
        section_id = parseInt(el.attr('data-sid'), 10)

        validator.set_data(selection.data)
        if validator.conflicts_with(section_id)
            console.log('obvious conflict')
            return false

        if is_checked
            selection.add_section(course_id, section_id)
        else
            selection.remove_section(course_id, section_id)
        validator.set_data(selection.data)

        if not validator.is_valid()
            selection.undo()
            console.log('deep conflict!')
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
        time = Time.parse_military(period.end).int() - Time.parse_military(period.start).int();
        #return 25 // 30 min time block
        #return 41.666666667 // 50 min time block
        return time / 3600.0 * height
}

# selected courses
$ ->
    target = $('#selected_courses')
    return unless target.length
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

        schedules = @response.result.schedules
        dows = @response.result.days_of_the_week
        time_range = @response.result.time_range

        if schedules.length
            target.empty()
            color_map = create_color_map(schedules[0], 8)
            for i in [0..schedules.length - 1]
                schedule = schedules[i]
                secs = []

                for section_id in schedule
                    secs.push(@sections.get(section_id).to_hash())

                timemap = create_timemap(schedule, @sections, dows, time_range)
                height = parseInt($('#thumbnail_template').attr('data-period-height'), 10)
                # render thumbnail
                target.append(templates.thumbnail_template(
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
                if options.selected_index == i
                    height = parseInt($('#schedule_template').attr('data-period-height'), 10)
                    $('#schedules').html(templates.schedule_template(
                        sid: i + 1 #response.result.id
                        schedules: schedules
                        dows: @response.result.days_of_the_week
                        timemap: timemap
                        time_range: @response.result.time_range
                        color_map: color_map
                        courses: @courses
                        sections: @sections
                        departments: @departments
                        crns: _.pluck(secs, (section) -> section.crn)
                        displayTime: template_functions.display_time
                        pluralize: template_functions.pluralize
                        period_height: (p) -> template_functions.period_height(p, height)
                        period_offset: (p) -> template_functions.period_offset(p, height)
                        humanize_hour: (h) ->
                            h = h % 12
                            apm = if h >= 12 then 'pm' else 'am'
                            if h == 0
                                '12 ' + apm
                            else
                                h + ' ' + apm
                        humanize_time: (time) ->
                            time = Time.parse_military(time)
                            time.format('{{ hour }}')
                    ))
            bind_schedule_events()
        else
            $('#schedules').html(templates.no_schedules_template())
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

    $('.view-schedules').click(->
        $('#thumbnails').toggle(200)
        return false
    )
    $('#thumbnails .select-schedule').live('click', ->
        schedule_id = parseInt($(this).parent().attr('data-sid'), 10) - 1
        display_schedules(
            selected_index: schedule_id
        )
        hide_schedules()
        return false
    )
    window.display_schedules = display_schedules
    window.current_schedule = current_schedule

# schedules view
$ ->
    target = $('#thumbnails')
    return unless target.length

    # requires browser support
    if History.enabled
        History.Adapter.bind(window, 'statechange', ->
            state = History.getState()
            if state.id
                display_schedules(
                    id: state.id
                    selected_index: state.index
                )
                return
        )

    display_schedules(
        section_ids: selection.get_sections()
        selected_index: 0
    )

