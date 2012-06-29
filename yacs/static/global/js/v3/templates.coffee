# searches for templates in the given page
# searches for script tags with type="text/template"
window.find_templates = (elements) ->
    elements ?= $('script[type="text/template"]')
    templates = {}
    $(elements).each(->
        $this = $(this)
        templates[$this.attr('id')] = _.template($this.html())
    )
    templates

