
# represents all models fetched from the API
class Model
    constructor: (@attrs) ->
        @attrs ?= {}
        @id = @attrs.id

    get: (name, defvalue) -> @attrs[name] or defvalue
    set: (name, value) -> @attrs[name] = value
    set_attributes: (attrs) -> $.extend(@attrs, attrs)
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
    attr: (name) ->
        [item[name] for item in @data]
    add: (item) ->
        @data.push(item)
        @id_map[item.id] = item
    clear: ->
        @slice(0)
        @id_map = {}
    get: (id) -> @id_map[id]
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
    constructor: () ->
        @base_url = '/api/4/'
        @filter = ''

    url: (object, id) ->
        if id?
            @base_url + object + '/' + id + '/'
        else
            @base_url + object + '/'

    get: (url, success, error) ->
        $.ajax({
            url: url
            type: 'GET'
            data: @filter
            dataType: 'json'
            cache: true
            success: (data) ->
                if data.success
                    if _.isArray(data.result)
                        collection = new Collection(url)
                        [collection.add(new Model(x, url + x.id + '/')) for x in data.result]
                        success(collection)
                    else
                        success(new Model(data.result, url))
                else
                    error(data, null)
            error: (xhr, txtStatus, exception) ->
                error(null, exception)
        })

    filter: (query) ->
      # TODO: fixme
      this

    semesters: (success, error) -> @get(@url('semesters'), success, error)
    departments: (success, error) -> @get(@url('departments'), success, error)
    courses: (success, error) -> @get(@url('courses'), success, error)
    sections: (success, error) -> @get(@url('sections'), success, error)
    conflicts: (success, error) -> @get(@url('conflicts'), success, error)

window.api = api = new API

