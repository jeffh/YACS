describe('FunctionsContext', function(){
  var NS = FunctionsContext;

  describe('time_parts', function(){
    it('should return an object of a hh:mm:ss format', function(){
      var result = NS.time_parts('12:30:22');
      expect(result).toEqual({
        hour: 12,
        minute: 30,
        second: 22
      });
    });

    it('should always convert integers into base 10', function(){
      var result = NS.time_parts('02:03:06');
      expect(result).toEqual({
        hour: 2,
        minute: 3,
        second: 6
      });
    });
  });

  describe('time_to_seconds', function(){
    it('should return seconds of string in format hh:mm:ss', function(){
      var result = NS.time_to_seconds('11:20:10');
      expect(result).toEqual(11 * 3600 + 20 * 60 + 10);
    });

    it('should assume the time is in base 10', function(){
      var result = NS.time_to_seconds('01:05:09');
      expect(result).toEqual(1 * 3600 + 5 * 60 + 9);
    });
  });

  describe('create_color_map', function(){
    it('should return an object mapping from course_id to index', function(){
      // we don't use the values
      var schedule = {
        1: null,
      2: null,
      4: null,
      5: null
      };

      var mapping = NS.create_color_map(schedule);
      expect(mapping).toEqual({
        1: 1,
        2: 2,
        4: 3,
        5: 4
      });
    });

    it('should recycle color numbers if more courses than colors', function(){
      // we don't use the values
      var schedule = {
        1: null,
      2: null,
      4: null,
      5: null
      };

      var mapping = NS.create_color_map(schedule, 2);
      expect(mapping).toEqual({
        1: 1,
        2: 2,
        4: 1,
        5: 2
      });
    });
  });

  describe('humanize_time', function(){
    it('should return a 12-hour time format from hh:mm:ss format', function(){
      var result = NS.humanize_time('05:20:13');
      expect(result).toEqual('5:20AM');
    });

    it('should return a 12-hour time format when hour > 12', function(){
      var result = NS.humanize_time('14:20:13');
      expect(result).toEqual('2:20PM');
    });

    it('should return 12-midnight for 00:00:00', function(){
      var result = NS.humanize_time('00:00:00');
      expect(result).toEqual('12AM');
    });

    it('should return 12-noon for 12:00:00', function(){
      var result = NS.humanize_time('12:00:00');
      expect(result).toEqual('12PM');
    });
  });

  describe('humanize_hour', function(){
    it('should return 4 pm for 16', function(){
      var result = NS.humanize_hour(16);
      expect(result).toEqual('4 pm');
    });

    it('should return 12-midnight for 0', function(){
      var result = NS.humanize_hour(0);
      expect(result).toEqual('12 am');
    });

    it('should return 12-noon for 12', function(){
      var result = NS.humanize_hour(12);
      expect(result).toEqual('12 pm');
    });
  });

  // these are functions for visual purposes and are highly
  // dependent on the stylesheet
  xdescribe('get_period_offset');
  xdescribe('get_period_height');
});
