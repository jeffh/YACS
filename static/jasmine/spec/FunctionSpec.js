describe('Function.bind', function(){
  it('should return function with given value binded to this', function(){
    var spy = function(){
      expect(this).toEqual('hello');
    };
    var fn = spy.bind('hello');
    fn();
  });

  it('should pass all arguments', function(){
    var spy = function(){
      expect(this).toEqual('hello');
      // we can't compare arguments to an array
      expect(arguments[0]).toEqual(1);
      expect(arguments[1]).toEqual(2);
      expect(arguments[2]).toEqual('abc');
    };
    var fn = spy.bind('hello')
    fn(1, 2, 'abc');
  });
});
