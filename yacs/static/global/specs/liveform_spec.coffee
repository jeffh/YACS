describe 'liveform', ->
    it 'should invoke callback when form changes', ->
        form = document.createElement('form')
        form.action = '/'
        form.method = 'POST'
        $(form).append('<input type="text" name="name" value="" />')
        spy = jasmine.createSpy()
        liveform(form, changed: spy)
        # simlulate key change
        form.name.value = 'john'
        $(form.name).trigger('keyup')
        expect(spy).toHaveBeenCalledWith($(form))

    it 'should invoke empty callback if form is reset', ->
        form = document.createElement('form')
        form.action = '/'
        form.method = 'POST'
        $(form).append('<input type="text" name="name" value="" />')
        spy = jasmine.createSpy()
        liveform(form, empty: spy)
        # simlulate key change
        $(form.name).val('foo').trigger('keyup')
        $(form.name).val('').trigger('keyup')
        expect(spy.callCount).toEqual(1)

    it 'should not invoke callback if form data does not change', ->
        form = document.createElement('form')
        form.action = '/'
        form.method = 'POST'
        $(form).append('<input type="text" name="name" value="" />')
        spy = jasmine.createSpy()
        liveform(form, changed: spy)
        # simlulate key change
        $(form.name).trigger('keyup')
        $(form.name).val('foo').trigger('keyup')
        $(form.name).val('foo').trigger('keyup')
        expect(spy.callCount).toEqual(1)

describe 'form_for_ajax', ->
    it 'returns an object of form information', ->
        spyOn($.fn, 'serialize').andCallFake(->
            return 'name=john doe'
        )
        form = document.createElement('form')
        form.action = '/submit'
        form.method = 'POST'
        $(form).append('<input type="text" name="name" value="john doe" />')
        data = form_for_ajax(form)
        expect(data).toEqual(
            url: '/submit'
            type: 'POST'
            data: 'name=john doe'
            cache: false
        )

describe 'updateform', ->
    it 'should perform ajax request on form change', ->
        form = document.createElement('form')
        form.action = '/submission'
        form.method = 'POST'
        $(form).append('<input type="text" name="name" value="" />')
        spyOn($, 'ajax').andCallFake((options) ->
            expect(options.url).toEqual('/submission')
            expect(options.type).toEqual('POST')
            options.success('foobar2000')
        )
        spyOn(window, 'delayfn').andCallFake((msec, fn) -> fn)
        events = {
            start: jasmine.createSpy()
            ajax_start: jasmine.createSpy()
            error: jasmine.createSpy()
            update: jasmine.createSpy()
        }

        updateform(form, events)

        $(form.name).val('john').trigger('keyup')
        expect(events.start).toHaveBeenCalled()
        expect(events.ajax_start).toHaveBeenCalled()
        expect(events.update).toHaveBeenCalledWith('foobar2000')
        expect($.ajax).toHaveBeenCalled()
        expect(window.delayfn).toHaveBeenCalled()

    it 'should invoke empty callback on empty form', ->
        form = document.createElement('form')
        form.method = form.action = 'ignore'
        $(form).append('<input type="text" name="name" value="" />')
        spyOn($, 'ajax').andCallFake((options) -> options.success('foobar'))
        events = {
            empty: jasmine.createSpy()
        }

        updateform(form, events)

        $(form.name).trigger('keyup')

        expect(events.empty).toHaveBeenCalledWith($(form))


    it 'should abort current request for a new one', ->
        runs ->
            form = document.createElement('form')
            form.method = form.action = 'ignore'
            $(form).append('<input type="text" name="name" value="" />')
            spyOn($, 'ajax').andCallFake((options) -> options.success('foobar'))
            @events = {
                start: jasmine.createSpy()
                ajax_start: jasmine.createSpy()
                error: jasmine.createSpy()
                update: jasmine.createSpy()
            }

            updateform(form, $.extend({}, @events, delay: 1))

            $(form.name).val('john').trigger('keyup')
            $(form.name).val('johnn').trigger('keyup')

        waits(3)
        runs ->
            expect(@events.start.callCount).toEqual(2)
            expect(@events.ajax_start.callCount).toEqual(1)
            expect(@events.error.callCount).toEqual(0)
            expect(@events.update.callCount).toEqual(1)
            expect(@events.update).toHaveBeenCalledWith('foobar')


    it 'should call error on failure', ->
        runs ->
            form = document.createElement('form')
            form.method = form.action = 'ignore'
            $(form).append('<input type="text" name="name" value="" />')
            spyOn($, 'ajax').andCallFake((options) ->
                setTimeout((-> options.error()), 1)
                return 1
            )
            spyOn(window, 'delayfn').andCallFake((msec, fn) -> fn)
            @events = {
                error: jasmine.createSpy()
                update: jasmine.createSpy()
            }

            updateform(form, @events)

            $(form.name).val('john').trigger('keyup')
        waits(2)
        runs ->
            expect(@events.error).toHaveBeenCalled()

