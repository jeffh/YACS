$.extend($.fn, {
    # provides checkbox shortcuts. Automatically filters by checkboxes
    # and radio buttons.
    # checked() -> Returns if the checkbox is checked or not
    # checked(bool) -> Sets checkbox to true or false
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
