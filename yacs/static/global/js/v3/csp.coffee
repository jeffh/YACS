
# performs a cartesian product
# based on the python psudeocode implementation
product = (arrays...) ->
    result = [[]]
    for array in arrays
        tmp = []
        for x in result
            for y in array
                newarr = x[...]
                newarr.push(y)
                tmp.push(newarr)
        result = tmp
    result

# basic brute force implementation
brute_force = (problem, options) ->
    options = $.extend({
        max_results: 0
    }, options)
    variables = problem.variables()
    domains = problem.domains()
    results = []
    for solution_values in product.apply(null, domains)
        solution = problem.create_solution(solution_values)
        results.push(solution) if problem.satisfies(solution)
        if options.max_results > 0 and options.max_results <= results.length
            return results
    results

class Problem
    constructor: (options) ->
        options = $.extend({}, options)
        @space = $.extend({}, options.variables)
        @constraints = options.constraints or []
        @solver = options.solver or brute_force
        console.warn('Improperly defined Problem') unless @is_valid()

    # self-checks if the problem is properly defined
    is_valid: ->
        for domain in @domains()
            return false unless $.type(domain) == 'array'
        for constraint in @constraints
            return false unless $.isFunction(constraint)
        return true

    # Returns all the variables names in the problem space
    variables: -> Object.keys(@space)
    # Returns all the domain values for the problem space
    domains: -> (@space[x] for x in @variables())

    # creates an object of values mapping to variables in the order
    # specified in Problem.variables()
    # Optionally, the ordering of variables can be specified to override
    # the default order.
    create_solution: (values, variables) ->
        variables ?= @variables()
        result = {}
        for i in [0...variables.length]
            result[variables[i]] = values[i]
        result

    # checks if a given solution satifies the stored constraints
    # uses Problem.create_solution() if the given solution is an array
    # Returns true if this solution is valid. False otherwise
    satisfies: (solution) ->
        if $.type(solution) == 'array'
            solution = @create_solution(solution)
        for c in @constraints
            unless c(solution)
                return false
        return true

@CSP = {
    Problem: Problem
    bruteForce: brute_force
    product: product
}
