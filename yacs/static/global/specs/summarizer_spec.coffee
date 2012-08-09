describe 'summarize', ->
  it 'shortens large amounts of text', ->
    p = document.createElement('p')
    $(p).text('this is a lot of text. No, really.')
    summarize(p, summary_length: 5)
    expect($(p).text()).toEqual('this ... (more)')
    # simulate clicking on the "read more" link
    handler = $(p).data('summarize-click-handler')
    handler.apply($(p).find('.read-more').get(0))
    expect($(p).text()).toEqual('this is a lot of text. No, really.')

  it 'does nothing for short text', ->
    p = document.createElement('p')
    $(p).text('The cake is a lie')
    summarize(p)
    expect($(p).text()).toEqual('The cake is a lie')
