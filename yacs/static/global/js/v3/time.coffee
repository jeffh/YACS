class Time
  # stores time in military format
  constructor: (properties, minute, second) ->
    if typeof(properties) != 'object'
      properties = {
        hour: properties
        minute: minute
        second: second
      }
    properties ?= {}
    @hour = parseInt(properties.hour, 10) or 0
    @minute = parseInt(properties.minute, 10) or 0
    @second = parseInt(properties.second, 10) or 0
    fmt = '{{ unit }} must be between 0 and {{ max }} (inclusive)'
    assert(@hour < 23 and @hour >= 0, format(fmt, unit: 'hour', max: 23))
    assert(@minute < 60 and @minute >= 0, format(fmt, unit: 'minute', max: 59))
    assert(@second < 60 and @second >= 0, format(fmt, unit: 'second', max: 59))

  format: (fmt, options) ->
    options = $.extend({
      sep: ':'
    }, options)
    left_padding = (n, padding, char) ->
      char ?= ' '
      str = '' + n
      while str.length < padding
        str = char + str
      str
    format(fmt,
      mhour: @hour
      zmhour: left_padding(@hour, 2, '0')
      hour: @standardHour()
      zhour: left_padding(@standardHour(), 2, '0')
      min: @minute
      zmin: left_padding(@minute, 2, '0')
      sec: @second
      zsec: left_padding(@second, 2, '0')
      sep_if_min: if @minute then options.sep else ''
      sep_if_sec: if @second then options.sep else ''
      min_if_min: if @minute then @minute else ''
      sec_if_sec: if @second then @second else ''
      zmin_if_min: if @minute then left_padding(@minute, 2, '0') else ''
      zsec_if_sec: if @second then left_padding(@second, 2, '0') else ''
      apm: if @isAM() then 'am' else 'pm'
      upper_apm: if @isAM() then 'AM' else 'PM'
      cap_apm: if @isAM() then 'Am' else 'Pm'
    )

  standardHour: ->
    h = @hour % 12
    if h == 0
      12
    else
      h

  isPM: -> @hour >= 12
  isAM: -> not @isPM()

Time.parse_military = (string) ->
  parts = string.split(':')
  console.log(parts)
  new Time(parts[0], parts[1], parts[2])

@Time = Time
