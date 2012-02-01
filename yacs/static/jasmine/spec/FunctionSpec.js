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

describe('Function.comp', function(){
  it('should save first argument', function(){
    var add = function(a, b){ return a + b; };
    var add1 = add.comp(1);
    expect(add1(2)).toEqual(3);
  });

  it('should save multiple arguments', function(){
    var add = function(a, b, c){ return a + b - c; };
    var add1 = add.comp(1, 4);
    expect(add1(2)).toEqual(3);
  });

  it('should retain function context', function(){
    var add = function(a, b){
      expect(this).toEqual('foobar');
    };
    var add1 = add.comp(1);
    add1.call('foobar', 1);
  });
});
