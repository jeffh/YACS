describe 'getCookie', ->
    it 'should extract value from cookie string', ->
        cookie = 'foo=bar;name=joe;rofl=coptor'
        expect(getCookie('foo', cookie)).toEqual('bar')
        expect(getCookie('name', cookie)).toEqual('joe')
        expect(getCookie('rofl', cookie)).toEqual('coptor')

    it 'should return null if no key exists in cookie string', ->
        expect(getCookie('foo', '')).toBeNull()

describe 'product', ->
    it 'should return an array with one empty array with no args', ->
        expect(product()).toEqual([[]])

    it 'should return an array with original array of possibilities', ->
        expect(product([1, 2, 3])).toEqual([[1], [2], [3]])

    it 'should create product with multiple arrays', ->
        expect(product([1, 2, 3], [4, 5])).toEqual([
            [1, 4],
            [1, 5],
            [2, 4],
            [2, 5],
            [3, 4],
            [3, 5],
        ])

describe 'iterate', ->
    it 'should loop over items asynchronously', ->
        runs ->
            @eachfn = jasmine.createSpy().andCallFake (item, index) ->
                @i ?= 5
                expect([index, item]).toEqual([@i - 5, @i])
                @i++

            @endfn = jasmine.createSpy().andCallFake ->
                expect(@i).toEqual(10)

            iterate([5..9], {
                delay: 1
                each: @eachfn
                end: @endfn
            })

        waits(10)
        runs ->
            expect(@eachfn.callCount).toEqual(5)
            expect(@endfn).toHaveBeenCalled()

    it 'should be cancellable', ->
        runs ->
            @end = jasmine.createSpy()
            job = iterate([0...5], {
                delay: 1
                each: jasmine.createSpy()
                end: @end
            })
            job.abort()
        waits(10)
        runs ->
            expect(@end.callCount).toEqual(0)


describe 'pushUnique', ->
    it 'inserts item if it does not exist in the array and return true', ->
        a = [1, 2, 3]
        expect(pushUnique(a, 4)).toBeTruthy()
        expect(a).toEqual([1, 2, 3, 4])

    it 'does nothing if the item already exists in the array and return false', ->
        a = [1, 2, 3]
        expect(pushUnique(a, 2)).toBeFalsy()
        expect(a).toEqual([1, 2, 3])

describe 'format', ->
    it 'does nothing to format string only', ->
        expect(format('foo {{ 0 }}')).toEqual('foo {{ 0 }}')

    it 'formats based on positional arguments', ->
        expect(format('foo {{ 0 }} {{ 1 }}', 'bar', 'cake')).toEqual('foo bar cake')

    it 'formats even with undefined values', ->
        expect(format('foo {{ 0 }} {{ 1 }}', undefined, null)).toEqual('foo <undefined> <null>')

    it 'formats based on object hash', ->
        expect(format('{{ hello }} {{ world }}', hello: 'goodbye', world: 'everyone')).toEqual('goodbye everyone')

describe 'hash_by_attr', ->
    it 'can flatten array of objects to an object', ->
        items = [
            {name: 'bob'},
            {name: 'jane'},
        ]
        result = hash_by_attr(items, 'name', flat: true)
        expect(result).toEqual(
            bob: {name: 'bob'},
            jane: {name: 'jane'}
        )

    it 'can categorize array of objects in to a hash', ->
        items = [
            {name: 'bob', id: 1},
            {name: 'jane', id: 2},
            {name: 'bob', id: 3},
        ]
        result = hash_by_attr(items, 'name')
        expect(result).toEqual(
            bob: [
                {name: 'bob', id: 1},
                {name: 'bob', id: 3},
            ]
            jane: [{name: 'jane', id: 2}]
        )

    it 'can use functions instead of keys', ->
        items = [
            {name: 'bob', id: 1},
            {name: 'jane', id: 2},
            {name: 'bob', id: 3},
        ]
        result = hash_by_attr(items, ((o) -> o.name), value: (o) -> o.id)
        expect(result).toEqual(
            bob: [1, 3]
            jane: [2]
        )


describe 'barrier', ->
    it 'invokes callback after number of invocations', ->
        spy = jasmine.createSpy()
        b = barrier(3, spy)
        b()
        b()
        expect(spy.callCount).toEqual(0)
        b()
        expect(spy.callCount).toEqual(1)

    it 'ignores further invocations', ->
        spy = jasmine.createSpy()
        b = barrier(1, spy)
        for i in [0...50]
            b()
        expect(spy.callCount).toEqual(1)

describe 'array_of_ints', ->
    it 'converts a sequence set of numbers into an array', ->
        items = array_of_ints('1, 2,3, 04')
        expect(items).toEqual([1, 2, 3, 4])

    it 'returns empty array for empty string', ->
        expect(array_of_ints('')).toEqual([])
