describe('Inspector.getProperties', function(){
  it('should return properties for an object, filtering Inspector extensions', function(){
    var obj = { foo: 'bar', lol: 1 };
    expect(new Inspector(obj).getProperties()).toEqual(['foo', 'lol']);
  })
});

describe('Inspector.getOwnProperties', function(){
  it('should return all owned properties', function(){
    var parnt = { foo: 'bar', length: 1 };
    var child = { lol: 1, foo: 2 };
    child.prototype = parnt;
    expect(new Inspector(child).getOwnProperties()).toEqual(['lol', 'foo', 'prototype']);
  });
});
