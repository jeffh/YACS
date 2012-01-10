describe('Object.getProperties', function(){
  it('should return properties for an object, filtering Object extensions', function(){
    var obj = { foo: 'bar', lol: 1 };
    expect(obj.getProperties()).toEqual(['foo', 'lol']);
  })
});

describe('Object.getAllProperties', function(){
  it('should return all properties for an object', function(){
    var obj = { foo: 'bar' };
    var expected = [
      'foo', 'getAllProperties', 'getProperties', 'getOwnProperties',
      'toInteger', 'toFloat'
    ];
    expect(obj.getAllProperties()).toEqual(expected);
  })
});

describe('Object.getOwnProperties', function(){
  it('should return all owned properties', function(){
    var parnt = { foo: 'bar', length: 1 };
    var child = { lol: 1, foo: 2 };
    child.prototype = parnt;
    expect(child.getOwnProperties()).toEqual(['lol', 'foo', 'prototype']);
  });
});

describe('Object.toInteger', function(){
  it('should convert integer', function(){
    expect('23'.toInteger()).toEqual(23);
  });

  it('should convert integer in base 10', function(){
    expect('023'.toInteger()).toEqual(23);
  });

  it('should allow custom base specified', function(){
    expect('11'.toInteger(2)).toEqual(3);
  });

  it('should return NaN on failure', function(){
    expect(isNaN('abc'.toInteger())).toBeTruthy();
  });
});

describe('Object.toFloat', function(){
  it('should convert integer', function(){
    expect('23.3'.toFloat()).toEqual(23.3);
  });

  it('should return NaN on failure', function(){
    expect(isNaN('abc'.toFloat())).toBeTruthy();
  });
});
