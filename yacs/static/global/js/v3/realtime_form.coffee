# realtime search
window.realtime_form = (form, target, options) ->
    options = $.extend({
        delay: 500
        request_start: $.noop
        event_start: $.noop
        success: $.noop
        error: $.noop
        cancel: $.noop
        complete: $.noop
        # the method that converts form data to be submitted
        serializer: (form, method) -> form.serialize()
        binder: (form, callback) -> # handles the binding of events
            $form = $(form).submit(callback)
            $form.find('input, textarea').keyup(callback)
            $form.find('select').change(callback)
            $form.find('input[type=search]').bind('search', callback)
    }, options)
    form = $(form)
    target = $(target)
    if not target.data('original-html')?
        target.data('original-html', target.html())
    perform_search = delayfn(options.delay, ->
        options.request_start()
        if form.data('realtime_form_request')?
            form.data('realtime_form_request').abort()
            Logger.info('cancelled prior ajax request.')

        request = $.ajax(form.attr('action'), {
            type: form.attr('method')
            data: options.serializer(form)
            success: (data) ->
                target.html(data)
                options.success()
            error: -> options.error()
            complete: ->
                form.data('realtime_form_request', null)
                options.complete()
        })
        form.data('realtime_form_request', request)
    )
    event_callback = ->
        options.event_start()
        perform_search()
    options.binder(form, event_callback)
