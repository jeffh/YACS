(function(undefined){

// requires: underscore
var root = this;
var prevValue = root.$U;
var u = root.$U = {};

var identity = function(a){ return a; }

// simple way to do asserts
var assert = u.assert = function(expr, msg){
  if (!expr)
    assert.raise(msg);
  return expr;
};
assert.raise = function(msg){ throw msg; };

// simple way to iterate over an extremely large collection of items without
// blocking the browser. This create many timeouts to allow the browser
// to render the user interface.
var iterate = u.iterate = function(collection, options){
  options = _.extend({}, {
    delay: 0.01,
    batchSize: 1000,
    batch: function(){},
    complete: function(){}
  }, options);
  for(var i=0, l=collection.length; i<l; i+=options.batchSize){
    setTimeout((function(start, stop){
      return function(){
        for(var j=start; j<stop; j++){
          options.each.call(collection[j], collection[j], j);
        }
        options.batch.call(collection, collection, start, stop);
      };
    })(i, Math.min(i + options.batchSize, l)), options.delay * i);
  }
  setTimeout(function(){
    options.complete.call(collection, collection);
  }, options.delay * collection.length);
};

// append(destArray, *arrays);
// Merges the given arrays into the destination array
var mergeArrays = u.mergeArrays = function(){
  var arrays = _.toArray(arguments);
  var destArr = arrays.shift();
  assert(destArr.push, "First argument must be an array.");
  _.each(arrays, function(array){
    _.each(array, function(value){
      destArr.push(value);
    });
  });
  return destArr;
};


// creates a function that invokes a given function based on a timeout.
var delayFunction = u.delayFunction = function(fn, timeout){
  var tid;
  return function() {
    if (tid) clearTimeout(tid);
    tid = setTimeout(fn, timeout);
  }
};


// Returns default value if the given value is undefined
var defaultsTo = u.defaultsTo = function(value, defaultValue){
  return (value === undefined) ? defaultValue : value;
}


// like python's collections.Counter class
var Counter = u.Counter = function(items, keyfn){
  var obj = {};
  var counts = {};
  _.extend(obj, {
    internal: counts,
    getCounts: function(){ return counts; },
    set: function(key, value){
      counts[key] = value;
      return obj;
    },
    get: function(key){ return defaultsTo(counts[key], 0); },
    increment: function(key){
      obj.set(key, obj.get(key) + 1);
      return obj;
    },
    decrement: function(key){
      obj.set(key, obj.get(key) - 1);
      return obj;
    },
    count: function(items, keyfn){
      keyfn = keyfn || identity;
      _.each(items || [], function(item){
        obj.increment(keyfn(item));
      });
      return obj;
    }
  });
  return obj.count(items, keyfn);
};

// short-hand for using Counter class
var count = u.count = function(items, keyfn){
  return Counter(items, keyfn).getCounts();
};


// simple string formatting. Use %s to designate strings to insert.
var format = u.format = function(){
  var args = _.toArray(arguments);
  var format_string = args.shift();
  var string;
  if (args.length === 1 && typeof args[0] === 'object' && format_string.indexOf('%s') < 0) {
    var named_args = args.shift();
    string = format_string.replace(/%\([A-Za-z0-9_$-]+\)?([%s])/g, function(_, name, kind, offset, full){
      if (kind === '%')
        return kind;
      assert(name !== undefined && named_args[name] !== undefined, "Expected named arg: " + name);
      return named_args[name];
    });
  } else {
    string = format_string.replace(/%([%s])/g, function(_, kind, offset, full){
      if (kind === '%')
        return kind;
      assert(args.length, "Expected more arguments based on formatted string: " + format_string);
      return args.shift();
    });
  }
  assert(!args.length, "Too many arguments based on formatted string: " + format_string);
  return string;
}


var range = u.range = function(stop){
  var arr = [];
  for(var i=0, l=arr.length; i<stop; i++){
    arr.push(i);
  }
  return arr;
};

// syncing / barrier / join: invokes a function after all "parts" are completed.
// parts are marked as completed by calling their individual notify methods
// from the returned array.
var Barrier = u.Barrier = function(options){
  options = _.extend({
    count: 2,
    sync: function(){},
    complete: function(){}
  }, options);
  var synced = {count: 0};
  return _.map(range(options.count), function(i){
    var obj = {
      hasNotified: false,
      notify: function(){
        if(obj.hasNotified)
          return;
        hasNotified = true;
        options.sync(synced.count + 1);
        if(++synced.count == options.count) options.complete();
      }
    };
    return obj;
  });
};


// an object of methods that would be good to extend another library object:
// such as jQuery's $ or underscore
u.extensions = function(obj){
  return {
    iterate: iterate,
    mergeArrays: mergeArrays,
    defaultsTo: defaultsTo,
    count: count
  };
}


})();

