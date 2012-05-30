
# represents all models fetched from the API
class Model
    constructor: (@attrs) ->
        @attrs ?= {}

    get: (name, defvalue) -> @attrs[name] or defvalue
    set: (name, value) -> @attrs[name] = value
    set_attributes: (attrs) -> $.extend(@attrs, attrs)
    replace_attributes: (attrs) -> @attrs = $.extend({}, attrs)
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
class Collection extends Array
    constructor: (@url) ->
    attr: (name) -> [item[name] for item in self]
    refresh: (options) ->
        options = options or {}
        success = options.success
        self = this
        url = options.url or @url
        $.ajax(
            $.extend({ url: url }, options, {
                success: (data) ->
                    self.splice(0, self.length)
                    self.push(item) for item in data.result
                    success(self)
            }))

# Public interface to accessing the API
class API
    constructor: () ->
        @base_url = '/api/4/'

    url: (object, id) ->
        if id?
            @base_url + object + '/' + id + '/'
        else
            @base_url + object + '/'

    get: (url, success, error) ->
        $.ajax({
            url: url
            type: 'GET'
            dataType: 'json'
            cache: true
            success: (data) ->
                if data.success
                    if _.isArray(data.result)
                        collection = new Collection(url)
                        [collection.push(new Model(x, url + x.id + '/')) for x in data.result]
                        success(collection)
                    else
                        success(new Model(data.result, url))
                else
                    error(data, null)
            error: (xhr, txtStatus, exception) ->
                error(null, exception)
        })

    semesters: (success, error) -> @get(@url('semesters'), success, error)
    departments: (success, error) -> @get(@url('departments'), success, error)
    courses: (success, error) -> @get(@url('courses'), success, error)
    sections: (success, error) -> @get(@url('sections'), success, error)

window.api = api = new API

