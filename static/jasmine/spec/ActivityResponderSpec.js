describe('ActivityResponder', function(){
  var events, ar;
  beforeEach(function(){
    events = {shown: 0, hidden: 0};
    ar = new ActivityResponder({
      show: function(){ events.shown++; },
      hide: function(){ events.hidden++; }
    });
  });

  describe('show', function(){
    it('should set state first', function(){
      ar.show();
      expect(events).toEqual({ shown: 1, hidden: 0 });
      expect(ar.isVisible()).toEqual(true);
    });

    it('should not repeat', function(){
      ar.show();
      ar.show();
      expect(events).toEqual({ shown: 1, hidden: 0 });
      expect(ar.isVisible()).toEqual(true);
    });
  });

  describe('hide', function(){
    beforeEach(function(){
      ar._currentState = true;
    });
    it('should call hide hook', function(){
      ar.hide();
      expect(events).toEqual({ shown: 0, hidden: 1 });
      expect(ar.isVisible()).toEqual(false);
    });

    it('should call hide consecutively', function(){
      ar.hide();
      ar.hide();
      expect(events).toEqual({ shown:0, hidden: 1 });
      expect(ar.isVisible()).toEqual(false);
    });
  });

  it('should allow alternating between show and hide', function(){
    ar.show();
    ar.hide();
    ar.show();
    expect(events).toEqual({
      shown: 2,
      hidden: 1
    });
    expect(ar.isVisible()).toEqual(true);
  });

  describe('setVisibility', function(){
    it('should allow explicitly setting visiblity', function(){
      ar.setVisibility(true);
      expect(events.shown).toEqual(1);
      expect(ar.isVisible()).toEqual(true);
    });

    it('should call show once if true multiple times', function(){
      ar.setVisibility(true);
      ar.setVisibility(true);
      expect(events).toEqual({ shown:1, hidden: 0 });
      expect(ar.isVisible()).toEqual(true);
    });
  });
});
