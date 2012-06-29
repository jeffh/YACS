class Storage
    constructor: (options) ->
        options = $.extend({}, options)
        # localStorage is more persistent.
        # sessionStorage will work for all systems (due to an extra library)
        @store = options.store or window.localStorage or window.sessionStorage
        @serialize = options.serialize or JSON.stringify
        @deserialize = options.deserialize or $.parseJSON
        @version = options.version or 4

    set: (key, value) -> @store.setItem(key, @serialize(value))
    get: (key) -> @deserialize(@store.getItem(key))
    clear: -> @store.clear()
    version_check: ->
        if @get('version') != @version
            Logger.warn(format(
                'Invalid version (got {{ 0 }}; expected {{ 1 }})',
                @get('version'), @version
            ))
            @clear()
            @set('version', @version)
        this

# Like Storage, but does absolutely nothing
class NullStorage
    set: (key, value) ->
    get: (key) ->
    clear: ->
    version_check: ->

class Selection
    constructor: (options) ->
        options = $.extend({}, options)
        @storage = options.storage or new Storage()
        @storage.version_check()
        @data = options.data or {}
        @conflicts = options.conflicts
        @history = []

    copy: ->
        new Selection(
            storage: new NullStorage()
            data: $.extend({}, @data) # clone
            conflicts: @conflicts
        )

    fetch_conflicts: ->
        that = this
        api.conflicts (data) -> that.conflicts = data
        that

    load: ->
        @data = @storage.get('selection')
        $(this).trigger('loaded', {sender: this, data: @data})
        this

    save: ->
        @storage.set('selection', @data)
        $(this).trigger('saved', {sender: this, data: @data})
        this

    undo: ->
        if @history.length
            @history.pop()()

    add_section: (course_id, section_id) ->
        @data[course_id] ?= []
        pushUnique(@data[course_id], section_id)
        that = this
        @history.push(->
            that.remove_section(course_id, section_id)
        )
        @save()

    add_course: (course_id, section_ids) ->
        @data[course_id] ?= []
        for sid in section_ids
            pushUnique(@data[course_id], sid)
        that = this
        @history.push(->
            that.remove_section(course_id, section_ids)
        )
        @save()

    remove_section: (course_id, section_id) ->
        if @data[course_id]?
            @data[course_id] = _.without(@data[course_id], section_id)

        if @data[course_id].length == 0
            delete @data[course_id]
        @save()

    remove_course: (course_id, section_ids) ->
        delete @data[course_id]
        @save()

    clear: ->
        @data = {}
        @save()

    has_courses: -> @get_sections().length != 0

    get_sections: ->
        sections = []
        for cid in Object.keys(@data)
            for sid in @data[cid]
                sections.push(sid)
        _.uniq(sections)

    get_courses: ->
        courses = []
        for cid in Object.keys(@data)
            courses.push(parseInt(cid, 10))
        courses

class Validator
    constructor: (options) ->
        options = $.extend({}, options)
        @data = options.data or {}
        @sections = null
        @conflicts = null

    set_data: (data) ->
        @data = data or {}
        this

    is_ready: -> @data? and @conflicts?

    set_conflicts: (conflicts) ->
        @conflicts = conflicts
        this

    set_sections: (sections) ->
        @sections = hash_by_attr(sections.to_array(),
            'id',
            value: (o) -> o.get('section_times')
            flat: true
        )
        this

    # checks if a given section id conflicts with the given selection
    # it does not check for cyclic conflicts
    # Use is_valid() to check for cyclic conflicts
    conflicts_with: (section_id) ->
        assert(@conflicts?, 'conflicts is not assigned')
        conflicting_sections = @conflicts.get(section_id)
        return null if not conflicting_sections?
        conflicting_sections = conflicting_sections.get('conflicts')
        for course_id in Object.keys(@data)
            course_id = parseInt(course_id, 10)
            is_conflicted = false
            for sid in @data[course_id]
                if _.include(conflicting_sections, sid)
                    is_conflicted = true
                    break
            if is_conflicted
                return course_id
        return null

    # checks for selections & cyclic conflicts
    # this is much slower than conflicts_with()
    is_valid: ->
        time_to_int = (s) ->
            parts = s.split(':')
            n = parseInt(parts[2], 10)
            n += parseInt(parts[1], 10) * 60
            n += parseInt(parts[0], 10) * 3600
            return n

        time_conflict = (time1, time2) ->
            start1 = time_to_int(time1.start)
            end1 = time_to_int(time1.end)
            start2 = time_to_int(time2.start)
            end2 = time_to_int(time2.end)
            dow1 = time1.days_of_the_week
            dow2 = time2.days_of_the_week

            dow_equal = false
            for dow in dow1
                if _.include(dow2, dow)
                    dow_equal = true
                    break

            result = dow_equal and (
                start1 <= start2 <= end1 or
                start2 <= start1 <= end2 or
                start1 <= end2 <= end1 or
                start2 <= end2 <= end2
            )
            result

        times_conflict = (times1, times2) ->
            for time1 in times1
                n = 0
                for time2 in times2
                    n += 1 if time_conflict(time1, time2)
                if n == times2.length
                    return true
            return false

        keys = Object.keys(@data)
        return true if keys.length < 2

        sections = (@data[course_id] for course_id in keys)
        for schedules in product(sections...)
            for i in [0...schedules.length-1]
                section1_times = @sections[schedules[i]]
                for j in [i+1...schedules.length-1]
                    section2_times = @sections[schedules[j]]
                    if times_conflict(section1_times, section2_times)
                        return false
        return true

window.Validator = Validator
window.NullStorage = NullStorage
window.Storage = Storage
window.Selection = Selection
