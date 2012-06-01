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
    version: 2
    constructor: (options) ->
        @keys = []
        @options = $.extend({
            autoload: true
            keyFormat: 'net.jeffhui.{{ scope }}.{{ key }}'
            serialize: JSON.stringify
            deserialize: $.parseJSON
            store: null
        }, options or {})
        @load if @options.autoload

    load: ->
        raw = @_get(@_getFullKey('keys', {isPrivate: true}))
        console.log(raw)
        try
            @keys = @_deserialize(raw)
        catch error
            @keys = raw.split(',')
            if $.trim(@keys[0]) == ''
                @keys = []
        this

    getStore: ->
        if @options.store
            return @options.store
        if window.localStorage
            return window.localStorage
        return window.sessionStorage

    _get: (key) -> @getStore().getItem(key)
    _set: (key, strval) -> @getStore().setItem(key, strval)
    _remove: (key) -> @getStore().removeItem(key)
    _serialize: (str) -> @options.serialize(str)
    _deserialize: (str) -> @options.deserialize(str)
    _save: -> @_set(@_getFullKey('keys', {isPrivate: true}), @keys)

    _getFullKey: (name, options) ->
        opt = $.extend({isPrivate: false}, options)
        format(@options.keyFormat, {
            scope: if opt.isPrivate then 'private' else 'public'
            key: name
        })

    contains: (key) -> @keys.indexOf(key) >= 0

    set: (key, value) ->
        assert($.type(key) == 'string', 'key must be a string')
        fullKey = @_getFullKey(key)
        @_set(fullKey, @_serialize(value))
        pushUnique(@keys, key)
        @_save()

    get: (key) ->
        assert($.type(key) == 'string', 'key must be a string')
        fullKey = @_getFullKey(key)
        @_deserialize(@_get(fullKey))

    clear: ->
        for key in @keys
            fullKey = @_getFullKey(key)
            @_remove(fullKey)
        @_save()

class Selection
    constructor: (@data) ->
        @data ?= {}
    get: -> $.extend({}, @data)
    set: (data) ->
        @data = $.extend({}, data)
    toggle_course: (course_id, section_ids) ->
        if @data[course_id]?
            delete @data[course_id]
        else
            @data[course_id] = section_ids
    toggle_section: (course_id, section_id) ->
        if @data[course_id]? and @data[course_id].indexOf(section_id) >= 0
            @data[course_id] = _.without(@data[course_id], section_id)
        else
            @data[course_id] ?= []
            @data[course_id].push(section_id)
        # TODO: save to storage

window.MemoryBackend = MemoryBackend
window.Storage = Storage
