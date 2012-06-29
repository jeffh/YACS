# returns the given value for the name in the cookie string
window.getCookie = getCookie = (name, source) ->
    source ?= document.cookie
    if source && source != ''
        cookies = source.split(';')
        for c in cookies
            [rawName, value] = $.trim(c).split('=', 2)
            if rawName == name
                return decodeURIComponent(value)
    return null

# performs a cartesian product
window.product = (arrays...) ->
    result = [[]]
    for array in arrays
        tmp = []
        for x in result
            for y in array
                newarr = x[...]
                newarr.push(y)
                tmp.push(newarr)
        result = tmp
    result

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
            if values[index]?
                values[index]
            else if index < values.length
                type = $.type(values[index])
                if type == 'undefined'
                    '<undefined>'
                else if type == 'null'
                    '<null>'
                else
                    '<unknown>'
            else
                match
        )

# convert an array to a dictionary mapping the given attribute name to
# an array whose attribute value are equal.
#
# Pass {flat: true} to options to force only one element
# (and no arrays as values of the dict).
#
# Pass {value: 'attr'} to options to set the return attribute value
# instead of being the array element. If the value is callable, then
# it is given the object in questioned and expects a value result
window.hash_by_attr = (array, attr, options) ->
    result = {}
    options ?= {}
    for item in array
        continue if not item?
        if $.isFunction(attr)
            key = attr(item)
        else
            key = item[attr]
        if options.value?
            if $.isFunction(options.value)
                value = options.value(item)
            else
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
    assert($.isFunction(complete), 'complete should be a function')
    i = 0
    return ->
        do (number) -> complete() if ++i == number


# breaks up loop work into separate async calls to prevent freezing
# the username
window.iterate = (array, options) ->
    options = $.extend({
        delay: 5
        context: {}
        each: (item, index) ->
        end: () ->
    }, options)
    job = {}
    $.extend(job, {
        is_running: true
        abort: -> job.is_running = false
    })
    callback = barrier(array.length, ->
        return unless job.is_running
        job.is_running = false
        options.end.call(options.context)
    )
    for i in [0...array.length]
        item = array[i]
        setTimeout((do (item, i) ->
            () ->
                return unless job.is_running
                options.each.call(options.context, item, i)
                callback()
        ), options.delay * i)
    job

# returns a new function that we only trigger after a given
# delay. Repeated calls before triggering will reset the timer.
window.delayfn = (msec, fn) ->
    timer = null
    return ((msec) ->
        return (args...) ->
            clearTimeout(timer)
            timer = setTimeout((-> fn(args...)), msec)
    )(msec)

# converts a string (from an html attr) to an array of integers
window.array_of_ints = (string) ->
    parts = string.split(',')
    numbers = []
    numbers.push(parseInt($.trim(x), 10)) for x in parts
    if numbers and numbers.length == 1 and isNaN(numbers[0])
        []
    else
        numbers

# wrapper around logging
window.Logger =
    NONE: 0
    CONSOLE: 1
    SERVER: 2
    USER: 3
    enabled: true
    log: (type, message...) ->
        if not Logger.enabled then return
        if not Logger.mode? then Logger.mode = Logger.CONSOLE
        if Logger.mode >= Logger.CONSOLE
            console[type].apply(console, message)
        if Logger.modemode >= Logger.SERVER
            # foo
            delayfn(200, () -> console.log(message...))()
        if Logger.modemode >= Logger.USER
            alert(' '.join(message))

    info: (message...) ->
        Logger.log('log', message...)

    warn: (message...) ->
        Logger.log('warn', message...)

    error: (message...) ->
        Logger.log('error', message...)

# modify ajax hook to send CSRF token for local requests
$(document).ajaxSend((evt, xhr, settings) ->
    sameOrigin = (url) ->
        host = document.location.host
        protocol = document.location.protocol
        sr_origin = '//' + host
        origin = protocol + sr_origin
        return (url == origin or url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            # or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url))

    safeMethod = (method) -> (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))

    if not safeMethod(settings.type) && sameOrigin(settings.url)
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'))
)

