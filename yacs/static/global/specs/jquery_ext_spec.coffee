describe '$.fn.checked', ->
    newInput = (type, checked) ->
        el = document.createElement('input')
        el.type = type
        if checked?
            el.checked = checked
        el

    it 'should return false for unchecked value', ->
        input = newInput('checkbox')
        ignored_input = newInput('checkbox', 'checked')
        expect($([input, ignored_input]).checked()).toBeFalsy()

    it 'should return true for checked value', ->
        input = newInput('radio', 'checked')
        expect($(input).checked()).toBeTruthy()

    it 'should check all checkboxes and radios if given true', ->
        input1 = newInput('checkbox')
        input2 = newInput('radio')
        p = document.createElement('p')
        selection = $([input1, input2, p])

        expect(selection.checked(true)).toEqual(selection)
        expect(input1.checked).toBeTruthy()
        expect(input2.checked).toBeTruthy()
        expect(p.checked).toBeUndefined()

    it 'should uncheck all checkboxes and radios if given false', ->
        input1 = newInput('checkbox', 'checked')
        input2 = newInput('radio', 'checked')
        p = document.createElement('p')
        selection = $([input1, input2, p])

        expect(selection.checked(false)).toEqual(selection)
        expect(input1.checked).toBeFalsy()
        expect(input2.checked).toBeFalsy()
        expect(p.checked).toBeUndefined()
