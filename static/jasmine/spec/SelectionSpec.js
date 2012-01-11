describe('Selection', function(){
  var sel, target;
  var G = function(selector){ return target.find(selector).get(0); };
  beforeEach(function(){
    target = $('<div id="target" style="display:none"></div>').appendTo(document.body);
    target.append(
      '<div class="course">' +
        '<input type="checkbox" id="selected_course_1" data-cid="1" data-crns="1, 2, 3" data-crns-full="3" />' +
        '<div class="sections">' +
          '<input type="checkbox" id="selected_course_1_1" data-cid="1" data-crn="1" />' +
          '<input type="checkbox" id="selected_course_1_2" data-cid="1" data-crn="2" />' +
          '<input type="checkbox" id="selected_course_1_3" data-cid="1" data-crn="3" />' +
        '</div>' +
      '</div>'
    );
    sel = new Selection();
  });

  afterEach(function(){
    target.remove();
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

    describe('add method', function(){
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
  });

  describe('Remove from selection', function(){
    it('should remove course id and non-full CRNs when calling removeCourse', function(){
      sel.set({ 1: [1, 2, 3], 2: [3, 4] });

      sel.removeCourse(G('#selected_course_1'));
      expect(sel.crns).toEqual({2: [3, 4]});
    });

    it('should remove CRN when calling removeSection', function(){
      sel.set({ 1: [1, 2, 3] });

      sel.removeSection(G('#selected_course_1_2'));
      expect(sel.crns).toEqual({ 1: [1, 3] });
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

  describe('toQueryString', function(){
    it('should return query string object of selection', function(){
      sel.set({ 1: [1, 2, 3], 2: [4, 5] });
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

  describe('save', function(){
    beforeEach(function(){
      jasmine.Ajax.useMock();
      sel.options.saveURL = '/foobar/';
    });

    it('should do nothing to server on success', function(){
      sel.save();
      var request = mostRecentAjaxRequest();
      request.response({
        status: 200,
        responseText: 'ok'
      });
    });

    xit('should alert the user of server errors', function(){
      var oldAlert = alert;
      window.alert = jasmine.createSpy();

      sel.save();
      var request = mostRecentAjaxRequest();
      request.response({
        status: 500,
        responseText: ''
      });

      expect(alert).toHaveBeenCalledWith();
      window.alert = oldAlert;
    });

    xit('should undo selection changes for bad requests', function(){
      sel.save();
      var request = mostRecentAjaxRequest();
      request.response({
        status: 400,
        responseText: 'bad request'
      });
    });
  });
  describe('refresh', function(){
  });
});
