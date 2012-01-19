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

  describe('keys', function(){
    it('should return all properties owned by object, excluding prototype', function(){
      var parentObj = {c: 'foo'};
      var childObj = {1: 'a', a: 'b'};
      childObj.prototype = parentObj
      expect(Utils.keys(childObj)).toEqual(['1', 'a']);
    });
  });

  describe('values', function(){
    it('should return values for all owned properties, excluding prototype', function(){
      var parentObj = {c: 'foo'};
      var childObj = {1: 'a', a: 'b'};
      childObj.prototype = parentObj
      expect(Utils.values(childObj)).toEqual(['a', 'b']);
    });
  });
});
