# used to prevent attaching multiple live events
attached_live = false

# text summarization when viewing course descriptions
window.summarize = (elements, options) ->
    options = $.extend({
        summary_length: 150
        more_text: 'more'
    }, options)
    $(elements).each(->
        $el = $(this)
        text = $.trim($el.text())
        $el.data('full-text', text)
        if text.length > options.summary_length
            text = text[0...options.summary_length] + '... '
            $el.text(text)
            $el.append(format(
              '(<a href="#read-more" class="read-more">{{ text }}</a>)',
              text: options.more_text
            ))
    )
    if not attached_live
      handler = ->
          parent = $(this).parent()
          text = parent.data('full-text')
          parent.text(text)
          return false

      $(elements).data('summarize-click-handler', handler)
      $('.read-more').live('click', handler)
      attached_live = true

