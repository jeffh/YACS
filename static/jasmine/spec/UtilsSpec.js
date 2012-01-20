describe('Utils', function(){
  describe('integer', function(){
    it('should return integer of base 10', function(){
      expect(Utils.integer('010')).toEqual(10);
    });
  });

  describe('sendMessage', function(){
    it('should invoke method of object with args', function(){
      var obj = {foo: function(a, b){ return a + b; }};
      expect(Utils.sendMessage(obj, 'foo', [1, 2])).toEqual(3);
    });

    it('should ignore non-methods', function(){
      expect(Utils.sendMessage({}, 'foo', [1, 2])).toBeFalsy();
    });
  });
});
