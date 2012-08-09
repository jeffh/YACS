describe 'Time', ->
  describe 'constructor', ->
    it 'accepts options argument', ->
      t = new Time(hour: '03', minute: '04', second: '05')
      expect(t.hour).toEqual(3)
      expect(t.minute).toEqual(4)
      expect(t.second).toEqual(5)

    it 'accepts positional argument', ->
      t = new Time('3', '4', '5')
      expect(t.hour).toEqual(3)
      expect(t.minute).toEqual(4)
      expect(t.second).toEqual(5)

  describe 'determining AM/PM', ->
    it 'returns AM for 11', ->
      expect(new Time(hour: 11).isAM()).toBeTruthy()
      expect(new Time(hour: 11).isPM()).toBeFalsy()

    it 'returns PM for 12 (noon)', ->
      expect(new Time(hour: 12).isPM()).toBeTruthy()
      expect(new Time(hour: 12).isAM()).toBeFalsy()

    it 'returns AM for 12 (midnight)', ->
      expect(new Time(hour: 0).isAM()).toBeTruthy()
      expect(new Time(hour: 0).isPM()).toBeFalsy()

  it 'converts military hour to standard hour', ->
    expect(new Time(hour: 11).standardHour()).toEqual(11)
    expect(new Time(hour: 14).standardHour()).toEqual(2)

  describe 'enforces military time ranges in constructor', ->
    it 'asserts military hours', ->
      expect(->
        new Time(hour: 24)
      ).toThrow('hour must be between 0 and 23 (inclusive)')

      expect(->
        new Time(hour: -1)
      ).toThrow('hour must be between 0 and 23 (inclusive)')

    it 'asserts minutes', ->
      expect(->
        new Time(minute: 60)
      ).toThrow('minute must be between 0 and 59 (inclusive)')

      expect(->
        new Time(minute: -1)
      ).toThrow('minute must be between 0 and 59 (inclusive)')

    it 'asserts seconds', ->
      expect(->
        new Time(second: 60)
      ).toThrow('second must be between 0 and 59 (inclusive)')

      expect(->
        new Time(second: -1)
      ).toThrow('second must be between 0 and 59 (inclusive)')
