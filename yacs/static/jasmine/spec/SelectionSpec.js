describe('Selection', function(){
  var sel;
  var fakeStorage = {container:{},};
  fakeStorage = $.extend(fakeStorage, {
    set: function(key, value){
      fakeStorage.container[key] = value;
    },
    get: function(key){
      return fakeStorage.container[key];
    }
  });

  beforeEach(function(){
    fakeStorage.container = {};
    sel = new Selection({
      storage: fakeStorage
    });
  });

  describe('set', function(){
    it('should assign crns property as a clone', function(){
      var val = {1: [2, 3]};
      sel.set(val);
      expect(sel.crns).toEqual(val);
      expect(sel.crns).not.toBe(val);
    });
  });

  describe('getCourseIds', function(){
    it('should return empty array if empty', function(){
      expect(sel.getCourseIds()).toEqual([]);
    });

    it('should return course ids', function(){
      sel.set({ 1: [1, 2, 3], 2: [3, 4] });
      expect(sel.getCourseIds()).toEqual([1, 2]);
    });
  });

  describe('with elements', function(){
    var target = $('<div id="target" style="display:none"></div>');
    var G = function(selector){ return target.find(selector).get(0); };
    target.append(
      '<input type="checkbox" id="selected_course_1" data-cid="1" data-crns="1, 2, 3" data-crns-full="3" />' +
      '<div class="sections">' +
      '<input type="checkbox" id="selected_course_1_1" data-cid="1" data-crn="1" />' +
      '<input type="checkbox" id="selected_course_1_2" data-cid="1" data-crn="2" />' +
      '<input type="checkbox" id="selected_course_1_3" data-cid="1" data-crn="3" />' +
      '</div>'
    );

    beforeEach(function(){
      target.appendTo(document.body);
    });

    afterEach(function(){
      target.remove();
    });

    describe('Adding to selection', function(){
      it('should add course id and non-full CRNs when calling addCourse', function(){
        var result = sel.addCourse(G('#selected_course_1'));
        expect(result).toBeTruthy();
        expect(sel.crns).toEqual({1: [1, 2]});
      });

      it('should add CRN when calling addSection', function(){
        var result = sel.addSection(G('#selected_course_1_2'));
        expect(result).toBeTruthy();
        expect(sel.crns).toEqual({1: [2]});
      });

      it('should invoke addCourse for course element', function(){
        var el = G('#selected_course_1');
        spyOn(sel, 'addCourse');
        sel.add(el);
        expect(sel.addCourse).toHaveBeenCalledWith(el);
      });

      it('should invoke addSection for course element', function(){
        var el = G('#selected_course_1_2');
        spyOn(sel, 'addSection');
        sel.add(el);
        expect(sel.addSection).toHaveBeenCalledWith(el);
      });
    });

    describe('Remove from selection', function(){
      it('should remove course id and non-full CRNs when calling removeCourse', function(){
        sel.set({1: [1, 2, 3], 2: [3, 4]});

        sel.removeCourse(G('#selected_course_1'));
        expect(sel.crns).toEqual({2: [3, 4]});
      });

      it('should remove CRN when calling removeSection', function(){
        sel.set({1: [1, 2, 3]});

        sel.removeSection(G('#selected_course_1_2'));
        expect(sel.crns).toEqual({1: [1, 3]});
      });

      describe('remove method', function(){
        it('should invoke removeCourse for course element', function(){
          var el = G('#selected_course_1');
          spyOn(sel, 'removeCourse');
          sel.remove(el);
          expect(sel.removeCourse).toHaveBeenCalledWith(el);
        });

        it('should invoke removeSection for course element', function(){
          var el = G('#selected_course_1_2');
          spyOn(sel, 'removeSection');
          sel.remove(el);
          expect(sel.removeSection).toHaveBeenCalledWith(el);
        });
      });
    });
  });

  describe('toQueryString', function(){
    it('should return query string object of selection', function(){
      sel.set({1: [1, 2, 3], 2: [4, 5]});
      var result = sel.toQueryString();
      expect(result).toEqual({
        'selected_course_1': 'checked',
        'selected_course_1_1': 'checked',
        'selected_course_1_2': 'checked',
        'selected_course_1_3': 'checked',
        'selected_course_2': 'checked',
        'selected_course_2_4': 'checked',
        'selected_course_2_5': 'checked'
      });
    });
  });

  describe('save and load', function(){
    var storage;
    beforeEach(function(){
      //jasmine.Ajax.useMock();
      storage = sel.options.storage = {
        set: function(k, v){ },
        get: function(k, v){ }
      };
    });

    it('should load from storage', function(){
      var selection = {1: [1, 2, 3], 2: [4, 5]};
      spyOn(storage, 'get').andReturn(selection);
      spyOn(sel, '_isValidVersion').andReturn(selection);

      expect(sel.load().crns).toEqual(selection);
    });

    it('should save to storage', function(){
      spyOn(storage, 'set').andReturn(null);

      var selection = { 1: [1, 2, 3], 2: [4, 5] };
      sel.set(selection);
      sel.save();

      expect(storage.set).toHaveBeenCalledWith('crns', selection);
    });
  });

  describe('refresh', function(){

  });
});
