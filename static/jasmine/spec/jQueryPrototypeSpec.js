describe('sandbox setup', function(){
  var target;
  beforeEach(function(){
    target = $('<div id="target"></div>').appendTo(document.body);
  });
  afterEach(function(){
    target.remove();
  });
  var G = function(selector){
    return target.find(selector);
  };

  describe('jQuery.fn.checked with no args (getter)', function(){
    it('should return true if input is checked', function(){
      target.append('<input id="test" type="checkbox" checked="checked" />');
      expect(G('#test').checked()).toBeTruthy();
    });

    it('should return boolean value of first input.', function(){
      target.append('<input type="checkbox" class="test" name="cb1" checked="checked" />' + 
        '<input type="checkbox" class="test" name="cb2" />');
      expect(G('.test').checked()).toBeTruthy();
    });

    it('should return false checked if unchecked.', function(){
      target.append('<input id="test" type="checkbox" />');
      expect(G('#test').checked()).toBeFalsy();
    });

    it('should return false checked if not input.', function(){
      target.append('<p id="test"></p>');
      expect(G('#test').checked()).toBeFalsy();
    });

    it('should return boolean value of first input.', function(){
      target.append('<p class="test"></p><input type="checkbox" checked="checked" class="test" />');
      expect(G('.test').checked()).toBeTruthy();
    });
  });

  describe('jQuery.fn.checked with arg (setter)', function(){
    it('should do nothing to non-checkbox elements', function(){
      target.append('<p id="p1"></p>' +
        '<p id="p2"></p>');
      var elems = G('p').checked(true);
      expect(elems).toEqual(elems);
      expect(elems.get(0).checked).toBeUndefined();
      expect(elems.get(1).checked).toBeUndefined();
    });

    it('should set checked attr of all input[type=checkbox]', function(){
      target.append('<input type="checkbox" id="p1" />' +
        '<input type="checkbox" id="p2" />');
      var elems = G('input').checked(true);
      expect(elems).toEqual(elems);
      expect(elems.get(0).checked).toBeTruthy();
      expect(elems.get(1).checked).toBeTruthy();
    });

    it('should only apply to input[type=checkbox] elements', function(){
      target.append('<p></p>',
        '<input type="checkbox" id="p1" />' +
        '<input type="checkbox" id="p2" />');
      var elems = G('input, p').checked(true);
      expect(elems).toEqual(elems);
      expect($(elems.get(0)).attr('checked')).toBeUndefined();
      expect(elems.get(1).checked).toBeTruthy();
      expect(elems.get(2).checked).toBeTruthy();
    });

    it('should remove checked attr when set to false', function(){
      target.append('<input type="checkbox" id="p1" checked="checked" />' +
        '<input type="checkbox" id="p2" checked="checked" />');
      var elems = G('input').checked(false);
      expect(elems).toEqual(elems);
      expect(elems.get(0).checked).toBeFalsy();
      expect(elems.get(1).checked).toBeFalsy();
    });
  });
});
