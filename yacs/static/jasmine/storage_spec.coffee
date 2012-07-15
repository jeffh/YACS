
describe 'storage', ->
    storage = null
    beforeEach ->
        storage = {
            setItem: jasmine.createSpy()
            getItem: jasmine.createSpy().andReturn('1')
            clear: jasmine.createSpy()
        }

    it 'should store a key value pairs', ->
        s = new Storage(store: storage)
        s.set('foo', 1)
        expect(storage.setItem).toHaveBeenCalledWith('foo', '1')
        expect(s.get('foo')).toEqual(1)
        expect(storage.getItem).toHaveBeenCalledWith('foo')

    it 'should clear existing storage if version does not match', ->
        s = new Storage(
            store: storage
            version: 2
        )
        s.version_check()
        expect(storage.getItem).toHaveBeenCalledWith('version')
        expect(storage.clear).toHaveBeenCalled()
        expect(storage.setItem).toHaveBeenCalledWith('version', '2')

describe 'selection', ->
    storage = null
    beforeEach ->
        storage = {
            version_check: jasmine.createSpy()
            set: jasmine.createSpy()
            get: jasmine.createSpy()
        }

    it "should track changes to user's set of sections", ->
        s = new Selection(storage: storage)
        saved = jasmine.createSpy()
        loaded = jasmine.createSpy()
        $(s).bind('saved', saved)
        s.add_section(1, 1)
        s.add_section(1, 1)
        s.add_section(1, 2)
        s.remove_section(1, 2)
        s.add_course(2, [3, 4])
        expect(s.get_sections()).toEqual([1, 3, 4])
        expect(s.get_courses()).toEqual([1, 2])
        expect(s.has_courses()).toBeTruthy()
        s.clear()
        expect(s.get_sections()).toEqual([])
        expect(s.get_courses()).toEqual([])
        expect(s.has_courses()).toBeFalsy()

        expect(storage.version_check).toHaveBeenCalled()
        expect(storage.set).toHaveBeenCalled()
        expect(saved).toHaveBeenCalled()

    it 'can copy itself', ->
        s1 = new Selection(
            storage: storage
            data: {
                1: [1, 2]
                2: [3, 4]
            }
        )
        s2 = s1.copy()
        expect(s1.get_courses()).toEqual(s2.get_courses())
        expect(s1.get_sections()).toEqual(s2.get_sections())

    it 'can undo last addition', ->
        s = new Selection(storage: storage)
        s.add_section(1, 1)
        s.add_section(1, 2)
        s.add_section(2, 3)
        expect(s.get_sections()).toEqual([1, 2, 3])
        expect(s.get_courses()).toEqual([1, 2])
        s.undo()
        expect(s.get_sections()).toEqual([1, 2])
        expect(s.get_courses()).toEqual([1])
        s.undo()
        expect(s.get_sections()).toEqual([1])
        expect(s.get_courses()).toEqual([1])
        s.undo()
        expect(s.get_sections()).toEqual([])
        expect(s.get_courses()).toEqual([])
        s.undo() # ensure no error occurs if can't undo anymore

    it 'should be able to load from storage', ->
        storage = {
            version_check: jasmine.createSpy()
            set: jasmine.createSpy()
            get: jasmine.createSpy().andReturn({1: [2,3], 2: [4, 5]})
        }
        s = new Selection(storage: storage)
        loaded = jasmine.createSpy()
        $(s).bind('loaded', loaded)
        s.load()
        expect(loaded).toHaveBeenCalled()
        expect(storage.get).toHaveBeenCalledWith('selection')
        expect(s.get_sections()).toEqual([2, 3, 4, 5])
        expect(s.get_courses()).toEqual([1, 2])

describe 'validator', ->
    describe 'internal helpers', ->
        v = null
        beforeEach ->
            v = new Validator()

        describe 'time_conflict', ->
            it 'should return true on conflicting times', ->
                expect(v._time_conflict(
                    { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                    { start: '10:00:00', end: '11:50:00', days_of_the_week: ['Monday'] }
                )).toBeTruthy()

            it 'should return false on non-conflicting times', ->
                expect(v._time_conflict(
                    { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                    { start: '11:00:00', end: '11:50:00', days_of_the_week: ['Monday'] }
                )).toBeFalsy()

            it 'should return false on non-conflicting days of the week', ->
                expect(v._time_conflict(
                    { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                    { start: '10:00:00', end: '11:50:00', days_of_the_week: ['Tuesday'] }
                )).toBeFalsy()

        describe 'section_times_conflict', ->
            it 'should return true for sections that do conflict', ->
                result = v._section_times_conflict([
                    { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                ], [
                    { start: '10:00:00', end: '11:50:00', days_of_the_week: ['Monday'] }
                ])
                expect(result).toBeTruthy()

            it 'should return true for multiple sections that do conflict', ->
                result = v._section_times_conflict([
                    { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                    { start: '10:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                ], [
                    { start: '10:00:00', end: '11:50:00', days_of_the_week: ['Monday'] }
                ])
                expect(result).toBeTruthy()

            it 'should return false if times do not conflict', ->
                result = v._section_times_conflict([
                    { start: '14:00:00', end: '16:50:00', days_of_the_week: ['Monday'] },
                    { start: '12:00:00', end: '13:50:00', days_of_the_week: ['Monday'] },
                ], [
                    { start: '10:00:00', end: '11:50:00', days_of_the_week: ['Monday'] }
                ])
                expect(result).toBeFalsy()

        describe 'schedule_is_valid', ->
            it 'should return false if sections do conflict', ->
                result = v._schedule_is_valid({
                    1: { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                    2: { start: '10:00:00', end: '11:50:00', days_of_the_week: ['Monday'] }
                })
                expect(result).toBeFalsy()

            it 'should return true if sections do not conflict', ->
                result = v._schedule_is_valid({
                    1: { start: '09:00:00', end: '10:50:00', days_of_the_week: ['Monday'] },
                    2: { start: '13:00:00', end: '14:50:00', days_of_the_week: ['Monday'] }
                })
                expect(result).toBeTruthy()

    it 'returns course id for invalid course', ->
        v = new Validator(
            data: {
                1: [1, 2, 5]
                2: [3]
            }
        ).set_conflicts(new API.Collection().add_array([
            # section id to many section_ids
            new API.Model({ id: 1, conflicts: [1, 2, 3] })
            new API.Model({ id: 2, conflicts: [1, 4] })
            new API.Model({ id: 3, conflicts: [1] })
            new API.Model({ id: 4, conflicts: [2] })
            new API.Model({ id: 5, conflicts: [] })
        ]))
        expect(v.conflicts_with(6)).toBeNull()
        expect(v.conflicts_with(5)).toBeNull()
        expect(v.conflicts_with(3)).toEqual(1)
        expect(v.conflicts_with(4)).toEqual(1)

    describe 'detect cyclic conflicts', ->
        describe 'with simple conflicts', ->
            sections = null
            beforeEach ->
                sections = new API.Collection().add_array([
                    new API.Model({ id: 1, section_times: [
                        {start: '10:00:00', end: '11:00:00', days_of_the_week: ['Monday']}
                        {start: '12:00:00', end: '14:00:00', days_of_the_week: ['Monday']}
                    ]})
                    new API.Model({ id: 2, section_times: [{start: '12:00:00', end: '13:00:00', days_of_the_week: ['Monday']}]})
                    new API.Model({ id: 3, section_times: [{start: '10:00:00', end: '11:00:00', days_of_the_week: ['Monday']}]})
                ])

            it 'should validate if only one conflict', ->
                v = new Validator(
                    data: {
                        1: [1]
                        2: [2]
                    }
                ).set_sections(sections)
                expect(v.is_valid()).toBeTruthy()

            it 'should not validate if no possible schedules', ->
                v = new Validator().set_data({
                    1: [1]
                    2: [2]
                    3: [3]
                }).set_sections(sections)
                expect(v.is_valid()).toBeFalsy()

        it 'should validate if different day of the week', ->
            sections = new API.Collection().add_array([
                new API.Model({ id: 1, section_times: [
                    {start: '10:00:00', end: '11:00:00', days_of_the_week: ['Tuesday']}
                    {start: '12:00:00', end: '14:00:00', days_of_the_week: ['Tuesday']}
                ]})
                new API.Model({ id: 2, section_times: [{start: '12:00:00', end: '13:00:00', days_of_the_week: ['Monday']}]})
                new API.Model({ id: 3, section_times: [{start: '10:00:00', end: '11:00:00', days_of_the_week: ['Monday']}]})
            ])
            v = new Validator().set_data({
                1: [1]
                2: [2]
                3: [3]
            }).set_sections(sections)
            expect(v.is_valid()).toBeTruthy()

        it 'should validate if there are more free sections', ->
            sections = new API.Collection().add_array([
                new API.Model({
                    id: 1,
                    section_times: [
                        {start: '10:00:00', end: '11:00:00', days_of_the_week: ['Monday']}
                        {start: '12:00:00', end: '14:00:00', days_of_the_week: ['Monday']}
                    ]
                })
                new API.Model({
                    id: 2,
                    section_times: [
                        {start: '15:00:00', end: '16:00:00', days_of_the_week: ['Tuesday']}
                    ]
                })
                new API.Model({ id: 3, section_times: [{start: '12:00:00', end: '13:00:00', days_of_the_week: ['Monday']}]})
                new API.Model({ id: 4, section_times: [{start: '10:00:00', end: '11:00:00', days_of_the_week: ['Monday']}]})
            ])
            v = new Validator().set_data({
                1: [1, 2]
                2: [3]
                3: [4]
            }).set_sections(sections)
            expect(v.is_valid()).toBeTruthy()

        it 'should return true on empty', ->
            v = new Validator().set_data()
            expect(v.is_valid()).toBeTruthy()


