# returns the given value for the name in the cookie string
window.getCookie = getCookie = (name) ->
    if document.cookie && document.cookie != ''
        cookies = document.cookie.split(';')
        for c in cookies
            cookie = $.trim(c)
            console.log(cookie[0..name.length], name + '=')
            if cookie[0..name.length] == name + '='
                return decodeURIComponent(cookie[(name.length + 1)..])
    return null

# simple assertion
window.assert = (bool, message) ->
    if not bool
        throw message || 'Assertion Failed'

# adds a given item to an array if it does not exist in the array.
# Returns true if added, false otherwise
window.pushUnique = (array, item) ->
    if array.indexOf(item) < 0
        array.push(item)
        true
    else
        false

# provides python-like string formatting.
#
# >>> format('{{ 0 }} {{ 1 }}', 'hello', 'world')
# 'hello world'
# >>> format('{{ foo }} {{ bar }}', {foo: 'goodbye', bar: 'cruel world'})
# 'goodbye cruel world'
window.format = (string, values...) ->
    if (values.length < 1)
        return string
    # process like named argument (names pair up with object properties)
    if values.length == 1 && $.type(values[0]) == 'object'
        obj = values[0]
        string.replace(/{{ *([a-zA-Z0-9_-]+) *}}/g, (match, identifer) ->
            if obj[identifer]? then obj[identifer] else match
        )
    else
        # process as numbered arguments (names pair up with argument indices)
        string.replace(/{{ *(\d+) *}}/g, (match, index) ->
            if values[index]? then values[index] else match
        )

# convert an array to a dictionary mapping the given attribute name to
# an array whose attribute value are equal.
#
# Pass {flat: true} to options to force only one element
# (and no arrays as values of the dict).
#
# Pass {value: 'attr'} to options to set the return attribute value
# instead of being the array element
window.dict_by_attr = (array, attr, options) ->
    result = {}
    for item in array
        key = item[attr]
        if options.value?
            value = item[options.value]
        else
            value = item
        if options.flat?
            result[key] = value
        else
            result[key] ?= []
            result[key].push(value)
    result


# returns a function can multiple async calls can invoke.
# once the given number of async calls has finished, invoke the callback.
# This is good for doing something after multiple ajax requests.
window.barrier = (number, complete) ->
    i = 0
    return do (number) ->
        complete() if ++i == number


# returns a new function that we only trigger after a given
# delay. Repeated calls before triggering will reset the timer.
window.delayfn = (msec, fn) ->
    timer = null
    return ((msec) ->
        return (args...) ->
            clearTimeout(timer)
            timer = setTimeout((-> fn(args...)), msec)
    )(msec)

window.set_difference = (original, toRemove) ->
    original = _.uniq(original)
    toRemove = _.uniq(toRemove)
    _.without(original, toRemove)

# wrapper around logging
window.Logger =
    CONSOLE: 1
    SERVER: 2
    USER: 3
    INFO: 1
    ERROR: 5
    enabled: true
    log: (type, message...) ->
        if not Logger.enabled then return
        if not Logger.mode? then Logger.mode = Logger.INFO
        if Logger.mode >= Logger.CONSOLE
            if type == Logger.INFO
                console.log(message...)
            else if type == Logger.ERROR
                console.error(message...)
        if Logger.modemode >= Logger.SERVER
            # foo
            delayfn(200, () -> console.log(message...))()
        if Logger.modemode >= Logger.USER
            alert(' '.join(message))

    info: (message...) ->
        Logger.log(Logger.INFO, message...)

    error: (message...) ->
        Logger.log(Logger.ERROR, message...)

# modify ajax hook to send CSRF token for local requests
$(document).ajaxSend((evt, xhr, settings) ->
    sameOrigin = (url) ->
        host = document.location.host
        protocol = document.location.protocol
        sr_origin = '//' + host
        origin = protocol + sr_originn
        return (url == origin or url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            # or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url))

    safeMethod = (method) -> (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))

    if not safeMethod(settings.type) && sameOrigin(settings.url)
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'))
)

