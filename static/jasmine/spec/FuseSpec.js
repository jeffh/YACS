describe('Fuse', function(){
  var fuse, events;
  beforeEach(function(){
    events = {triggered: 0, cancelled: 0};
    fuse = new Fuse({
      delay: 25,
      trigger: function(){ events.triggered++; },
      cancelled: function(){ events.cancelled++; }
    });
  });

  it('should fire trigger after 25 msec', function(){
    runs(function(){
      fuse.start();
    });
    waits(26);
    runs(function(){
      expect(events.triggered).toBeTruthy();
    });
  });

  it('should not fire trigger if stopped before 25 msec', function(){
    runs(function(){
      fuse.start();
    });
    waits(8);
    runs(function(){
      fuse.stop();
    });
    waits(26);
    runs(function(){
      expect(events.triggered).toBeFalsy();
    });
  });

  it('should fire trigger once if started multiple times under 25 msec', function(){
    runs(function(){ fuse.start(); });
    waits(8);
    runs(function(){ fuse.start();});
    waits(8);
    runs(function(){
      expect(events.triggered).toBeFalsy();
    });
    waits(25);
    runs(function(){
      expect(events.triggered).toBeTruthy();
    });
  });

  it('should trigger each if started multiple times spaced out more than 25 msec', function(){
    runs(function(){ fuse.start(); });
    waits(26);
    runs(function(){ fuse.start(); });
    waits(26);
    runs(function(){
      expect(events.triggered).toEqual(2);
    });
  });
});
