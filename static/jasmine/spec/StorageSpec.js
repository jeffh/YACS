describe('Storage', function(){
  var storage, store;
  var identity = function(val){ return val; };
  beforeEach(function(){
    store = {
      setItem: function(key, value){},
      getItem: function(key){},
      removeItem: function(key){}
    };

    storage = new Storage({
      store: store,
      serialize: identity,
      deserialize: identity,
      autoload: false,
      keyFormat: '{{ type }}.{{ key }}'
    });
  });

  it('should have no keys', function(){
    expect(storage.keys).toEqual([]);
  });

  it('can store a string to a key', function(){
    spyOn(store, 'setItem').andCallFake(function(key, value){
      expect(key).toEqual('public.foo');
      expect(value).toEqual('bar');
    });
    storage.set('foo', 'bar');
  });

  it('can retrieve a string from a key', function(){
    spyOn(store, 'getItem').andCallFake(function(key){
      expect(key).toEqual('public.foo');
      return 'bar';
    });
    expect(storage.get('foo')).toEqual('bar');
  });

  it('can load keys from storage', function(){
    spyOn(store, 'getItem').andCallFake(function(key){
      return ['a', 'b', 'c'];
    });
    storage.load();
    expect(storage.keys).toEqual(['a', 'b', 'c']);
  });

  it('can check for existance of its keys', function(){
    storage.keys = ['a', 'b', 'c'];
    expect(storage.contains('a')).toBeTruthy();
    expect(storage.contains('z')).toBeFalsy();
  });

  it('can clear storage', function(){
    spyOn(store, 'removeItem').andReturn(null);
    storage.keys = ['a', 'b', 'c'];
    storage.clear();

    expect(store.removeItem).toHaveBeenCalledWith('public.a');
    expect(store.removeItem).toHaveBeenCalledWith('public.b');
    expect(store.removeItem).toHaveBeenCalledWith('public.c');
  });
});
