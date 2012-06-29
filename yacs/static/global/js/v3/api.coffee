
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
        @filter = ''
        @cache = {}

    clear_cache: -> @cache = {}

    url: (object, id) ->
        if id?
            @base_url + object + '/' + id + '/'
        else
            @base_url + object + '/'

    get: (url, success, error) ->
        that = this
        success_callback = (data) ->
            that.cache[url] = data
            if data.success
                if _.isArray(data.result)
                  collection = new Collection(url)
                  [collection.add(new Model(x, url + x.id + '/')) for x in data.result]
                  success(collection)
                else
                  success(new Model(data.result, url))
            else
                error(data, null)

        if @cache[url]?
            success_callback(@cache[url])
            return null

        $.ajax({
            url: url
            type: 'GET'
            data: @filter
            dataType: 'json'
            cache: true
            success: success_callback
            error: (xhr, txtStatus, exception) ->
                error(null, exception)
        })

    filter: (query) ->
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

        if options.section_ids
            data = '?section_id=' + options.section_ids.join('&section_id=')
        else
            data = ''
        url = @url('schedules', options.id) + data
        if @cache[url]?
            success_callback(@cache[url])
            return null

        $.ajax({
            url: url
            type: 'GET'
            dataType: 'json'
            cache: true
            success: options.success
            error: options.error
        })

window.API = API
window.API.Model = Model
window.API.Collection = Collection
window.api = api = new API('/api/4/')

