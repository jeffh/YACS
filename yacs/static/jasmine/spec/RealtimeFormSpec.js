describe('RealtimeForm', function(){
  var target, GETform, POSTform;
  beforeEach(function(){
    target = $('<div id="target"></div>').appendTo(document.body);
    GETform = $('<form id="GETform" action="/action/get/" method="get"></form>').appendTo(target);
    POSTform = $('<form id="POSTform" action="/action/post/" method="post"></form>').appendTo(target);
  });

  afterEach(function(){
    target.remove();
  });

  describe('getURL', function(){
    it('should return action url', function(){
      var rt = new RealtimeForm(GETform);
      expect(rt.getURL()).toEqual('/action/get/');
    });

    it('should return action url from options if provided', function(){
      var rt = new RealtimeForm(POSTform, {url: '/override/'});
      expect(rt.getURL()).toEqual('/override/');
    });

    it('should append querystr for non-GET forms in additionalGET option', function(){
      var rt = new RealtimeForm(POSTform, {additionalGET: {foo: 'bar'}});
      expect(rt.getURL()).toEqual('/action/post/?foo=bar');
    });

    it('should append to querystring existing for non-GET form in additionalGET option', function(){
      var rt = new RealtimeForm(POSTform, {
        url: '/override/?search=1',
        additionalGET: {foo: 'bar'}
      });
      expect(rt.getURL()).toEqual('/override/?search=1&foo=bar');
    });
  });

  describe('getMethod', function(){
    it('should return method', function(){
      var rt = new RealtimeForm(GETform);
      expect(rt.getMethod()).toEqual('GET');

      rt = new RealtimeForm(POSTform);
      expect(rt.getMethod()).toEqual('POST');
    });

    it('should return method from options if provided', function(){
      var rt = new RealtimeForm(POSTform, {method: 'get'});
      expect(rt.getMethod()).toEqual('GET');
    });
  });

  describe('getMethodData', function(){
    var input = function(type, name, value){
      return $('<input type="'+type+'" name="'+name+'" value="'+value+'" />');
    }
    beforeEach(function(){
      GETform.append(
        input('search', 'search', 'foo')
      );
      POSTform.append(
        input('text', 'name', 'joe'),
        input('text', 'addr', '1 infinite loop')
      );
    });

    afterEach(function(){
      GETform.html('');
      POSTform.html('');
    });

    it('should return form data from GET form', function(){
      var actual = new RealtimeForm(GETform).getMethodData();
      expect(actual).toEqual('search=foo');
    });

    it('should return form data put additionalGET option', function(){
      var actual = new RealtimeForm(GETform, {
        additionalGET: {foo: 1, bar: 'lol'}
      }).getMethodData();
      expect(actual).toEqual('search=foo&foo=1&bar=lol');
    });

    it('should return form data from POST form', function(){
      var actual = new RealtimeForm(POSTform).getMethodData();
      expect(actual).toEqual('name=joe&addr=1+infinite+loop');
    });

    it('should return form data put additionalPOST option', function(){
      var actual = new RealtimeForm(GETform, {
        additionalGET: {foo: 1, bar: 'lol'}
      }).getMethodData();
      expect(actual).toEqual('search=foo&foo=1&bar=lol');
    });

    it('should throw exception on unknown form method', function(){
      var PUTform = $('<form method="put" action="/action/put/"></form>');
      expect(function(){
        new RealtimeForm(PUTform).getMethodData();
      }).toThrow('Invalid method type');
    });
  });
});
