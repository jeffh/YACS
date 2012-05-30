
# text summarization when viewing course descriptions
summarize = (elements, options) ->
    options = $.extend({
        summary_length: 150
    }, options)
    elements.each(->
        $el = $(this)
        text = $.trim($el.text())
        $el.data('full-text', text)
        if text.length > options.summary_length
            text = text[0...options.summary_length] + '... '
        $el.text(text)
        $el.append('(<a href="#read-more" class="read-more">more</a>)')
    )
    $('.read-more').live('click', ->
        parent = $(this).parent()
        text = parent.data('full-text')
        parent.text(text)
    )

$(-> summarize($('.summarize'), {summary_length: 150}))
