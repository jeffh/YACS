
# represents all models fetched from the API
class Model
    constructor: (@attrs) ->
        @attrs ?= {}
        @id = @attrs.id

    get: (name, defvalue) -> @attrs[name] or defvalue
    set: (name, value) -> @attrs[name] = value
    set_attributes: (attrs) -> $.extend(@attrs, attrs)
    to_hash: -> $.extend({}, @attrs)
    replace_attributes: (attrs) ->
        @attrs = $.extend({}, attrs)
        @id = @attrs.id
    refresh: (options) ->
        options = options or {}
        success = options.success or $.noop
        self = this
        $.ajax(
            $.extend({ url: @get('url') }, options, {
                success: (data) ->
                    self.replace_attributes(data.result)
                    success(self)
            }))

# represents collections of models fetched from the API
class Collection
    constructor: (@url) ->
        @id_map = {}
        @data = []
        @length = 0
    attr: (name) ->
        [item[name] for item in @data]
    add: (item) ->
        @data.push(item)
        @id_map[item.id] = item
        @length = @data.length
        this
    add_array: (arr) ->
        for item in arr
            @add(item)
        this
    clear: ->
        @slice(0)
        @id_map = {}
        @length = 0
        this
    get: (id) -> @id_map[id]
    to_array: -> @data.slice(0)
    refresh: (options) ->
        options = options or {}
        success = options.success
        self = this
        url = options.url or @url
        $.ajax(
            $.extend({ url: url }, options, {
                success: (data) ->
                    self.data.splice(0, self.length)
                    for item in data.result
                        self.add(item)
                    success(self)
            }))

# Public interface to accessing the API
class API
    constructor: (@base_url) ->
        @_filter = ''
        @cache = {}
        @callbacks = {}

    clear_cache: ->
      @cache = {}
      @callbacks = {}

    url: (object, id) ->
        if id?
            @base_url + object + '/' + id + '/'
        else
            @base_url + object + '/'

    _add_callbacks: (url, success, error) ->
        @callbacks[url] ?= {
          successes: []
          errors: []
          request: null
        }
        @callbacks[url].successes.push(success)
        @callbacks[url].errors.push(error)

    _invoke_callbacks: (url, type, args...) ->
        i = 0
        for fn in @callbacks[url][type]
            fn(args...)
            ++i
        @callbacks[url].successes = @callbacks[url].successes.slice(i)
        @callbacks[url].errors = @callbacks[url].errors.slice(i)

    get: (url, success, error) ->
        that = this
        success_callback = (data) ->
            that.cache[url] = data
            if data.success
                if _.isArray(data.result)
                  collection = new Collection(url)
                  [collection.add(new Model(x, url + x.id + '/')) for x in data.result]
                  that._invoke_callbacks(url, 'successes', collection)
                else
                  that._invoke_callbacks(url, 'successes', new Model(data.result, url))
            else
                that._invoke_callbacks(url, 'errors', data, null)

        @_add_callbacks(url, success, error)

        if @cache[url]?
            success_callback(@cache[url])
            return null

        unless @callbacks[url].request
          @callbacks[url].request = $.ajax({
            url: url
            type: 'GET'
            data: @_filter
            dataType: 'json'
            cache: true
            success: success_callback
            error: (xhr, txtStatus, exception) ->
              that._invoke_callbacks(url, 'errors', null, exception)
          })

    filter: (query) ->
      @_filter = $.param(query)
      this

    semesters: (success, error, id) -> @get(@url('semesters', id), success, error)
    departments: (success, error, id) -> @get(@url('departments', id), success, error)
    courses: (success, error, id) -> @get(@url('courses', id), success, error)
    sections: (success, error, id) -> @get(@url('sections', id), success, error)
    conflicts: (success, error, id) -> @get(@url('conflicts', id), success, error)
    schedules: (options) ->
        options = $.extend({
            id: null
            section_ids: null
            success: $.noop
            error: $.noop
            cache: true
        }, options)
        assert(options.id? or options.section_ids?, 'id or section_ids need to be specified')

        if options.section_ids and not options.id
            data = '?section_id=' + options.section_ids.join('&section_id=')
        else
            data = ''
        url = @url('schedules', options.id) + data

        @_add_callbacks(url, options.success, options.error)

        if @cache[url]?
            @_invoke_callbacks(url, 'successes', @cache[url])
            return null


        that = this
        $.ajax({
            url: url
            type: 'GET'
            dataType: 'json'
            cache: true
            success: (data) ->
                that._invoke_callbacks(url, 'successes', data)
            error: (xhr, type, exception) ->
                that._invoke_callbacks(url, 'errors', null, exception)
        })

window.API = API
window.API.Model = Model
window.API.Collection = Collection
window.api = api = new API('/api/4/')

