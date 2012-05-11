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
                    success(data.result)
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
