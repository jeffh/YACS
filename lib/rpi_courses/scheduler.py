from pyconstraints import Problem, is_nil, BruteForceSolver


__all__ = ['compute_schedules', 'TimeRange', 'Scheduler']


class TimeRange(object):
    "Represents a time range to be restricted."
    def __init__(self, start, end, dow):
        self.start = start
        self.end = end
        self.days_of_week = dow

    def __repr__(self):
        return "<TimeRange: %r to %r on %r>" % (
            self.start, self.end, self.days_of_week
        )

    def days_conflict(self, days):
        print self.days_of_week, days
        for day in self.days_of_week:
            if day in days:
                return True
        return False

    def __contains__(self, period):
        days, start, end = period

        return self.days_conflict(days) and (
            self.start <= start <= self.end or
            start <= self.start <= end or
            self.start <= end <= self.end or
            start <= self.end <= end
        )

    def conflicts_with(self, section):
        "Returns True if the given section conflicts with this time range."
        for p in section.periods:
            t = (p.int_days, p.start, p.end)
            if t in self:
                return True
        return False


def section_constraint(section1, section2):
    if is_nil(section1) or is_nil(section2):
        return True
    return not section1.conflicts_with(section2)


class Scheduler(object):
    """High-level API that wraps the course scheduling feature.

    ``free_sections_only``: bool. Determines if the only the available sections should be
                            used when using courses provided. Defaults to True.
    ``problem``: Optional problem instance to provide. If None, the default one is created.

    """
    def __init__(self, free_sections_only=True, problem=None, constraint=None):
        self.p = Problem()
        if problem is not None:
            self.p = problem
        self.free_sections_only = free_sections_only
        self.section_constraint = constraint or section_constraint
        self.clear_excluded_times()

    def clear_excluded_times(self):
        """Clears all previously set excluded times."""
        self._excluded_times = []
        return self

    def exclude_time(self, start, end, days):
        """Added an excluded time by start, end times and the days.

        ``start`` and ``end`` are in military integer times (e.g. - 1200 1430).
        ``days`` is a collection of integers or strings of fully-spelt, lowercased days
                 of the week.
        """
        self._excluded_times.append(TimeRange(start, end, days))
        return self

    def exclude_times(self, *tuples):
        """Adds multiple excluded times by tuple of (start, end, days) or by
        TimeRange instance.

        ``start`` and ``end`` are in military integer times (e.g. - 1200 1430).
        ``days`` is a collection of integers or strings of fully-spelt, lowercased days
                 of the week.
        """
        for item in tuples:
            if isinstance(item, TimeRange):
                self._excluded_times.append(item)
            else:
                self.exclude_time(*item)
        return self

    def find_schedules(self, courses=None, return_generator=False):
        """Returns all the possible course combinations. Assumes no duplicate courses.

        ``return_generator``: If True, returns a generator instead of collection. Generators
            are friendlier to your memory and save computation time if not all solutions are
            used.
        """
        self.p.reset()
        self.create_variables(courses)
        self.create_constraints(courses)
        if return_generator:
            return self.p.iter_solutions()
        return self.p.get_solutions()

    # internal methods -- can be overriden for custom use.
    def get_sections(self, course):
        """Internal use. Returns the sections to use for the solver for a given course.
        """
        return course.available_sections if self.free_sections_only else course.sections

    def time_conflict(self, schedule):
        """Internal use. Determines when the given time range conflicts with the set of
        excluded time ranges.
        """
        if is_nil(schedule):
            return True
        for timerange in self._excluded_times:
            if timerange.conflicts_with(schedule):
                return False
        return True

    def create_variables(self, courses):
        """Internal use. Creates all variables in the problem instance for the given
        courses. If given a dict of {course: sections}, will use the provided sections.
        """
        has_sections = isinstance(courses, dict)
        for course in courses:
            self.p.add_variable(course, courses.get(course, []) if has_sections else self.get_sections(course))

    def create_constraints(self, courses):
        """Internal use. Creates all constraints in the problem instance for the given
        courses.
        """
        for i, course1 in enumerate(courses):
            for j, course2 in enumerate(courses):
                if i <= j:
                    continue
                self.p.add_constraint(self.section_constraint, [course1, course2])
            self.p.add_constraint(self.time_conflict, [course1])


def compute_schedules(courses=None, excluded_times=(), free_sections_only=True, problem=None, return_generator=False, section_constraint=None):
    """
    Returns all possible schedules for the given courses.
    """
    s = Scheduler(free_sections_only, problem, constraint=section_constraint)
    s.exclude_times(*tuple(excluded_times))
    return s.find_schedules(courses, return_generator)
