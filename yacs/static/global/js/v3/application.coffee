# stop attaching hooks if we're in jasmine tests
return if $('.content').length == 0

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

validator = null
has_initialized = false
initialize_validator = ->
    return if has_initialized
    $('input[type=checkbox]').attr('disabled', 'disabled')
    callback = barrier(2, ->
        has_initialized = true
        $('input[type=checkbox]').removeAttr('disabled')
        console.log('loaded!')
    )
    api.conflicts((conflicts) ->
        validator.set_conflicts(conflicts)
        callback()
    )
    api.sections((sections) ->
        validator.set_sections(sections)
        callback()
    )

courses = null
$ -> api.courses((data) -> courses = data)

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
            sec2course = {}
            for section_id in section_ids
                cid = validator.conflicts_with(section_id)
                if cid?
                    conflicted_sections.push(section_id)
                    sec2course[section_id] = cid
                    console.log('conflicts', cid, course_id)
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
                course.append(templates.conflict_template(
                    classname: 'conflicts_with_course'
                    name: courses.get(sec2course[conflicted_sections[0]]).get('name')
                ))
                course.find('input[type=checkbox]').attr('disabled', 'disabled')
            else # per section conflict
                for section_id in conflicted_sections
                    continue if $('#section_' + section_id).checked()
                    section = $('#section_' + section_id).parent().addClass('conflict')
                    section.find('label').append(templates.conflict_template(
                        classname: 'conflicts_with_section'
                        name: courses.get(sec2course[section_id]).get('name')
                    ))
        end: -> conflict_runner = null
    })

# checkboxes for storage
$ ->
    window.selection = selection = new Selection()
    window.validator = validator = new Validator()
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


