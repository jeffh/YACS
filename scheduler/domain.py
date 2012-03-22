from csp import is_nil

from courses.utils import DAYS, sorted_daysofweek

from scheduler.scheduling import compute_schedules as _compute_schedules

class ConflictCache(object):
    _EMPTY_SET = frozenset()
    def __init__(self, conflict_mapping):
        self.conflict_mapping = conflict_mapping

    def __key__(self, section_id):
        return self.conflict_mapping.get(section_id, self._EMPTY_SET)

    def __call__(self, section1, section2):
        if is_nil(section1) or is_nil(section2):
            return True
        self.section_conflicts(section1.id, section2.id)

    def section_conflicts(self, section1_id, section2_id):
        return (
            section2_id in self[section1_id] or
            section1_id in self[section2_id]
        )



def has_schedule(selected_courses, section_constraint=None):
    schedules = _compute_schedules(
            selected_courses,
            free_sections_only=False,
            generator=True,
            section_constraint=section_constraint)
    for schedule in schedules:
        return True
    return False


def compute_schedules(selected_courses, section_constraint=None):
    """Returns the schedules in a JSON-friendly format.

    Returns a list of dictionary of course id to crns.
    """
    schedules = _compute_schedules(selected_courses,
            free_sections_only=False,)
            #section_constraint=section_constraint)
    results = []
    for schedule in schedules:
        s = {}
        for course, section in schedule.items():
            s[str(course.id)] = section.id
        results.append(s)
    return results

def period_stats(periods):
    if len(periods) < 1:
        return range(8, 20), DAYS[:5]
    min_time, max_time, dow_used = None, None, set()
    for period in periods:
        min_time = min(min_time or period.start, period.start)
        max_time = max(max_time or period.end, period.end)
        dow_used = dow_used.union(period.days_of_week)

    timerange = range(min_time.hour -1 , max_time.hour + 2)
    return list(timerange), sorted_daysofweek(dow_used)


