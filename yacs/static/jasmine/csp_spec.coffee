describe 'BruteForceSolver', ->
    it 'can solve a given problem given a problem instance', ->
        problem = {
            variables: -> ['x' ,'y']
            domains: -> [[1, 2, 3], [1, 2, 3]]
            create_solution: CSP.Problem::create_solution
            satisfies: (solution) -> solution.x < solution.y
        }
        result = CSP.bruteForce(problem)
        expect(result).toEqual([
            {x: 1, y: 2}
            {x: 1, y: 3}
            {x: 2, y: 3}
        ])

    it 'can restrict the number of results', ->
        problem = {
            variables: -> ['x' ,'y']
            domains: -> [[1, 2, 3], [1, 2, 3]]
            create_solution: CSP.Problem::create_solution
            satisfies: (solution) -> solution.x < solution.y
        }
        result = CSP.bruteForce(problem, max_results: 1)
        expect(result).toEqual([
            {x: 1, y: 2}
        ])

describe 'Problem', ->
    it 'can specify a constraints problem to solve', ->
        constraints = [
            jasmine.createSpy()
            jasmine.createSpy()
        ]
        p = new CSP.Problem(
            variables: {
                x: [1, 2, 3]
                y: [1, 2, 3]
            }
            constraints: constraints
        )
        expect(p.variables()).toEqual(['x', 'y'])
        expect(p.domains()).toEqual([ [1, 2, 3], [1, 2, 3] ])
        expect(p.constraints).toEqual(constraints)
        expect(p.create_solution([1, 2])).toEqual({x: 1, y: 2})
