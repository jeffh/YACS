describe 'find_templates', ->
    it 'return object of templated script tags', ->
        spyOn(_, 'template').andCallFake((raw) ->
            expect(raw).toEqual('hello <%= world %>!')
            return 'foo'
        )
        context = $('<script type="text/template" id="hello_world">hello <%= world %>!</script>')
        expect(find_templates(context)).toEqual(
            hello_world: 'foo'
        )

