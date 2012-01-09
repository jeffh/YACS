describe('Array.contains', function(){
  it('should return true if array contains item', function(){
    expect([1,2,3].contains(3)).toBeTruthy();
  });

  it('should return false if array does not contain item', function(){
    expect([1,2,3].contains(4)).toBeFalsy();
  });
});

describe('Array.map', function(){
  it('should be equal to identity mapped array', function(){
    var identity = function(value){ return value; };
    var arr = [1, 2, 3];
    expect(arr.map(identity)).toEqual(arr);
  });

  it('should build array of returned values', function(){
    var incr = function(value){ return value + 1; };
    var arr = [1, 2, 3];
    expect(arr.map(incr)).toEqual([2, 3, 4]);
  });

  it('should give value as this to fn', function(){
    var incr = function(){ return this + 1; };
    var arr = [1, 2, 3];
    expect(arr.map(incr)).toEqual([2, 3, 4]);
  });

  it('should give index as second arg to fn', function(){
    var incr = function(value, i){ return value + i; };
    var arr = [1, 2, 3];
    expect(arr.map(incr)).toEqual([1, 3, 5]);
  });
});

describe('Array.filter', function(){
  it('should be identity if fn is always true', function(){
    var truthy = function(){ return true; };
    var arr = [1, 2, 3];
    expect(arr.filter(truthy)).toEqual(arr);
  });

  it('should be empty if fn is always false', function(){
    var falsy = function(){ return false; }
    expect([1, 2, 3].filter(falsy)).toEqual([]);
  });

  it('should be dependent on fn return value', function(){
    var isEven = function(value){ return value % 2 === 0; };
    expect([1, 2, 3].filter(isEven)).toEqual([2]);
  });

  it('should give value as this to fn', function(){
    var isEven = function(){ return this % 2 === 0; };
    expect([1, 2, 3].filter(isEven)).toEqual([2]);
  });

  it('should give index as this to fn', function(){
    var isEven = function(value, i){ return i % 2 === 0; };
    expect([1, 2, 3].filter(isEven)).toEqual([1, 3]);
  });
});

describe('Array.pushUnique', function(){
  it('should add item to array if not in array already', function(){
    var arr = [1, 2];
    expect(arr.pushUnique(3)).toBeTruthy();
    expect(arr).toEqual([1, 2, 3]);
  });

  it('should not add item to array if not in array already', function(){
    var arr = [1, 2];
    expect(arr.pushUnique(2)).toBeFalsy();
    expect(arr).toEqual([1, 2]);
  });
});

describe('Array.unique', function(){
  it('should return new array sorted', function(){
    var arr = [3, 2, 1];
    var newarr = arr.unique();
    expect(arr).not.toBe(newarr);
    expect(newarr).toEqual([1, 2, 3]);
  });

  it('should return array with no duplicates', function(){
    var arr = [1, 1, 2, 3, 3, 3];
    expect(arr.unique()).toEqual([1, 2, 3]);
  });
});

describe('Array.excludeFrom', function(){
  it('should return new array with all items in first list that are not in the second one', function(){
    var a1 = [1, 2, 3];
    var a2 = [2, 3, 4];
    expect(a1.excludeFrom(a2)).toEqual([1]);
  });

  it('should return new array with unique items only and sorted', function(){
    var a1 = [3, 3, 4, 2, 2, 1];
    var a2 = [3, 4, 5];
    expect(a1.excludeFrom(a2)).toEqual([1, 2]);
  });
});

describe('Array.removeItem', function(){
  it('should remove item from array by value', function(){
    var arr = 'a b c'.split(' ');
    expect(arr.removeItem('b')).toBeTruthy();
    expect(arr).toEqual(['a', 'c']);
  });

  it('should remove all items from array by value', function(){
    var arr = 'a b b b c c'.split(' ');
    expect(arr.removeItem('b')).toBeTruthy();
    expect(arr).toEqual(['a', 'c', 'c']);
  });

  it('should return false if no items were removed', function(){
    var arr = 'a b c'.split(' ');
    expect(arr.removeItem('z')).toBeFalsy();
    expect(arr).toEqual(['a', 'b', 'c']);
  });
});
