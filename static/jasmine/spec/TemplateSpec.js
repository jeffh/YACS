describe('Template', function(){
  describe('with context', function(){
    var context = {
      num: 1,
      string: 'foobar',
      html: '<p>bar</p>',
      fn: function(a, b){ return a + b + this.num; }
    };

    it('should return string', function(){
      var t = new Template({string: 'foobar'});
      expect(t.render(context)).toEqual('foobar');
    });

    it('should return context values', function(){
      var t = new Template({string: '<%= num %>'});
      expect(t.render(context)).toEqual('1');
    });

    it('should return context value from function with context as context', function(){
      var t = new Template({string: '<%= fn(1, 2) %>'});
      expect(t.render(context)).toEqual('4');
    });

    it('should return context value with escaped html', function(){
      var t = new Template({string: '<%- html %>'});
      expect(t.render(context)).toEqual('&lt;p&gt;bar&lt;&#x2F;p&gt;');
    });

    it('should allow extended context', function(){
      var t = new Template({string: '<%= string %><%= num %><%= foo %>'});
      t.extendContext(context);
      expect(t.render({num: 2, foo: 'bar'})).toEqual('foobar2bar');
    });
  });

  describe('with no context', function(){
    it('should return string if no eval tags', function(){
      var t = new Template({string: 'foobar'});
      expect(t.render()).toEqual('foobar');
    });

    it('should support arbitrary javascript', function(){
      var t = new Template({string: '<% for(var i=0; i<4; i++){ %><%= i %><% } %>'});
      expect(t.render()).toEqual('0123');
    });

    it('should support string extration from element', function(){
      var el = $('<div id="temp">test</div>').appendTo(document.body);
      try {
        var t = new Template({selector: '#temp'});
        expect(t.render()).toEqual('test');
      } finally {
        el.remove();
      }
    });
  });
});
