$.extend($.fn, {
    # provides checkbox shortcuts
    checked: ->
        checkboxes = @filter('input[type=checkbox], input[type=radio]')
        if arguments.length < 1
            return checkboxes.attr('checked')?
        if arguments[0]
            checkboxes.attr('checked', 'checked')
        else
            checkboxes.removeAttr('checked')
        this
})
