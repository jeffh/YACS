# key-value store in memory. Not persistent
class MemoryBackend
    constructor: (@obj) ->
    setItem: (key, strval) -> @obj[key] = strval
    getItem: (key) -> @obj[key]
    removeItem: (key) ->
        val = @obj[key]
        delete @obj[key]
        val

class Storage
    version: 3
    constructor: (options) ->
        @options = $.extend({
            serialize: JSON.stringify
            deserialize: $.parseJSON
            store: null
        }, options or {})

    load: ->
        Logger.info('loaded from storage')
        curr_ver = @get('version')
        if isNaN(curr_ver) or curr_ver != @version
            msg = format(
                'Invalid version from store (got {{ old }}, expected {{ new }})',
                old: @get('version', 0)
                new: @version)
            Logger.warn(msg)
            if isNaN(curr_ver)
                @getStore().clear()
            @clear()
        @set('version', @version)
        this

    getStore: ->
        if @options.store
            return @options.store
        if window.localStorage
            return window.localStorage
        return window.sessionStorage

    keys: -> Object.keys(@getStore())

    contains: (key) -> @keys().indexOf(key) >= 0

    set: (key, value) ->
        assert($.type(key) == 'string', 'key must be a string')
        @getStore().setItem(key, @options.serialize(value))

    remove: (key) -> @getStore().removeItem(key)

    get: (key, default_value) ->
        assert($.type(key) == 'string', 'key must be a string')
        if @contains(key)
            try
                @options.deserialize(@getStore().getItem(key))
            catch error
                default_value
        else
            Logger.info('key missing, using default:', key)
            default_value

    clear: -> @getStore().clear()

ConflictDetector = (collection) ->
    get = (array, item) ->
        i = array.indexOf(item)
        if i >= 0
            array[i]
        else
            null
    comparer = (sid1, sid2) ->
        s1 = collection.get(parseInt(sid1, 10))
        s2 = collection.get(parseInt(sid2, 10))
        s1? and get(s1.get('conflicts'), sid2) or
            s2? and get(s2.get('conflicts'), sid1)
    comparer.update = (new_data) ->
        collection = new_data
        if new_data? and comparer.on_ready?
            comparer.on_ready()
    comparer.is_ready = -> collection?
    return comparer

class Selection
    constructor: (options) ->
        options = $.extend({
            data: null
            storage: (new Storage()).load()
            conflictor: null
        }, options)
        @conflicts_with = options.conflictor
        @storage = options.storage
        @data = options.data or @storage.get('selection', {})
        self = this
        conflictor.on_ready = -> self.validate()
        Logger.info('data', @data)
    clear: -> @data = {}
    get: (course_id) -> @data[course_id]
    set: (data) -> @data = $.extend({}, data)
    has_section_id: (sid) ->
      for cid in @course_ids()
        if _.includes(@get(cid), sid)
          return true
      return false
    save: -> @storage.set('selection', @data)
    course_ids: -> Object.keys(@data)
    is_empty: -> @course_ids().length == 0
    conflicts_with: (section_id) ->
        conflicts_with = null
        for cid in @data
            sids = @data[cid]
            conflict = -1
            for sid in sids
                conflict = @conflictor(sid, section_id)
                if not conflict?
                    break
            if conflict?
                conflicts_with =
                    course_id: parseInt(cid, 10),
                    section_id: conflict
                break
        if conflicts_with? and conflicts_with.section_id?
            return conflicts_with
        return null

    validate: ->
        section_ids = []
        for cid in Object.keys(@data)
            section_ids.push(@data[cid])
        schedules = product(section_ids)
        for schedule in schedules
            valid = true
            for i in [0...schedule.length - 1]
                for j in [i + 1...schedule.length]
                    if @conflicts_with(schedule[i], schedule[j])
                        valid = false
                        return false
        return schedules.length != 0

    # section_ids -> set of section_ids to associate with the given course_id
    #                if checked
    # return bool indicating if the given course_id has no sections checked
    toggle_course: (course_id, section_ids) ->
        if @data[course_id]?
            delete @data[course_id]
            @save()
            false
        else
            @data[course_id] = section_ids
            @save()
            true
    # return bool indicating course is empty or not
    toggle_section: (course_id, section_id) ->
        if @data[course_id]? and @data[course_id].indexOf(section_id) >= 0
            @data[course_id] = _.without(@data[course_id], section_id)
            if @data[course_id].length == 0
                delete @data[course_id]
                @save()
                return true
        else
            @data[course_id] ?= []
            @data[course_id].push(section_id)
        @save()
        false

window.MemoryBackend = MemoryBackend
window.Storage = Storage
window.Selection = Selection
window.ConflictDetector = ConflictDetector
