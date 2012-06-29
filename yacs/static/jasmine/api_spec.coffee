describe 'API', ->
    api = null
    beforeEach ->
        api = new API('/api/4/')
        @addMatchers(
            toEqualTo: (expected) ->
                if expected.equals?
                    expected.equals(@actual)
                else if @actual.equals?
                    @actual.equals(expected)
                else
                    @toEqual(expected)
        )

    it 'should fetch object without network problems', ->
      spyOn($, 'ajax').andCallFake((options) ->
        expect(options.url).toEqual('/api/4/semesters/1/')
        expect(options.cache).toBeTruthy()
        options.success({
          version: 4
          result: {
            name: "Spring Session 2012"
            year: 2012
            date_updated: "2012-04-29T15:36:17.836592"
            ref: "http://sis.rpi.edu/reg/zs201201.htm"
            id: 1
            month: 1
          }
          success: true
        })
      )
      api.semesters(((semester) ->
        expect(semester).toEqual(new API.Model(
          name: "Spring Session 2012"
          year: 2012
          date_updated: "2012-04-29T15:36:17.836592"
          ref: "http://sis.rpi.edu/reg/zs201201.htm"
          id: 1
          month: 1
        ))), null, 1)

    it 'should fetch collection without network problems', ->
        spyOn($, 'ajax').andCallFake((options) ->
            expect(options.url).toEqual('/api/4/semesters/')
            expect(options.cache).toBeTruthy()
            options.success({
                version: 4
                success: true
                result: [
                    {
                        name: "Fall Session 2012"
                        year: 2012
                        date_updated: "2012-04-29T15:36:37.148566"
                        ref: "http://sis.rpi.edu/reg/zs201209.htm"
                        id: 8
                        month: 9
                    },
                    {
                        name: "Spring Session 2012"
                        year: 2012
                        date_updated: "2012-04-29T15:36:17.836592"
                        ref: "http://sis.rpi.edu/reg/zs201201.htm"
                        id: 1
                        month: 1
                    }
                ]
            })
        )
        api.semesters((semesters) ->
            expect(semesters.to_array()).toEqual([
                new API.Model(
                    name: "Fall Session 2012"
                    year: 2012
                    date_updated: "2012-04-29T15:36:37.148566"
                    ref: "http://sis.rpi.edu/reg/zs201209.htm"
                    id: 8
                    month: 9
                ),
                new API.Model(
                    name: "Spring Session 2012"
                    year: 2012
                    date_updated: "2012-04-29T15:36:17.836592"
                    ref: "http://sis.rpi.edu/reg/zs201201.htm"
                    id: 1
                    month: 1
                )
            ])
        )

    it 'should invoke error callback with bad request', ->
      spyOn($, 'ajax').andCallFake((options) ->
        options.success(
          version: 4
          result: "I don't know"
          success: false
        )
      )
      api.semesters(null, (data, e) ->
        expect(e).toBeNull()
        expect(data).toEqual(
          version: 4
          result: "I don't know"
          success: false
        )
      )

    it 'should invoke error callback with no network', ->
      exception = jasmine.createSpy()
      spyOn($, 'ajax').andCallFake((options) ->
        xhr = jasmine.createSpy()
        status = 'test-error'
        options.error(xhr, status, exception)
      )
      api.semesters(null, (data, e) ->
        expect(data).toBeNull()
        expect(e).toEqual(exception)
      )

