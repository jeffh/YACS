# handles attaching to various form events
window.liveform = (form, options) ->
    options = $.extend({
        changed: (form) ->
        empty: $.noop
        listen: (form, callback) ->
            false_callback = ->
                callback()
                return false
            true_callback = ->
                callback()
                return true
            $(form).submit(false_callback)
            $(form).find('input, select').change(true_callback)
            $(form).find('input[type=text], input[type=search], textarea').keyup(true_callback)
            $(form).find('input[type=search]').bind('search', true_callback)
    }, options)
    $form = $(form)
    empty_state = previous = $form.serialize()
    options.listen($form, ->
        querystring = $form.serialize()
        if empty_state == querystring
            options.empty($form)
        else if querystring != previous
            options.changed($form)
        previous = querystring
    )

# serializes form data into an object for passing into $.ajax
window.form_for_ajax = (form) ->
    $form = $(form)
    {
        url: $form.attr('action')
        type: $form.attr('method').toUpperCase()
        data: $form.serialize()
        cache: $form.attr('method').toUpperCase() == 'GET'
    }

# uses live form to update form values
window.updateform = (form, options) ->
    options = $.extend({
        data: {}
        start: $.noop
        ajax_start: $.noop
        update: $.noop # accepts (html) parameter
        error: $.noop
        empty: $.noop
        delay: 200
    }, options)
    request = null
    trigger = delayfn(options.delay, ->
        if request?
            request.abort()
        ajax = form_for_ajax(form)
        ajax.data += '&' + $.param(options.data)
        request = $.ajax($.extend(ajax,
            success: (data) ->
                request = null
                options.update(data)
            error: ->
                if request?
                    options.error()
                    request = null
        ))
        options.ajax_start()
    )
    liveform(form,
        changed: ->
            options.start()
            trigger()
        empty: options.empty
    )

