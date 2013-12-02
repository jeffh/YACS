from django import template

from courses.utils import DAYS, ObjectJSONEncoder
from courses.encoder import default_encoder


register = template.Library()


def remove_zero_prefix(timestr):
    if timestr[0] == '0':
        return timestr[1:]
    return timestr


@register.filter
def bold_topics_include(string):
    return string.replace('Topics include', '<strong>Topics include</strong>')


@register.filter
def requires_truncation(string, summary_size):
    tstr = string.lower().strip()
    return len(tstr[:summary_size].strip()) != len(tstr.strip())


@register.filter
def reverse_truncatechars(string, start):
    """Inverse of truncate chars. Instead of the first x characters,
    excludes the first nth characters.
    """
    return string[start:]


@register.filter
def toJSON(obj):
    return ObjectJSONEncoder().encode(default_encoder.encode(obj))


@register.filter
def get(obj, key):
    if obj:
        try:
            return getattr(obj, key)
        except (AttributeError, TypeError):
            pass
        try:
            return obj[key]
        except (KeyError, IndexError):
            pass
    return None


@register.filter
def display_period(period):
    fmt = "%s-%s"
    start_format, end_format = "%I", "%I"
    if period.start.minute != 0:
        start_format += ':%M'
    if period.end.minute != 0:
        end_format += ':%M'
    end_format += " %p"
    return fmt % (
        remove_zero_prefix(period.start.strftime(start_format)).lower(),
        remove_zero_prefix(period.end.strftime(end_format)).lower(),
    )


@register.filter
def sort(iterable):
    return sorted(iterable)


@register.filter
def dow_short(dow):
    if isinstance(dow, list) or isinstance(dow, tuple):
        return tuple(map(dow_short, dow))
    return {
        'Monday': 'Mon',
        'Tuesday': 'Tue',
        'Wednesday': 'Wed',
        'Thursday': 'Thu',
        'Friday': 'Fri',
        'Saturday': 'Sat',
        'Sunday': 'Sun',
    }.get(dow)


@register.filter
def period_dow_buckets(periods):
    """Prepares periods by day of the week.
    """
    slots = {}
    for period in periods:
        for dow in period.days_of_week:
            slots.setdefault(dow, []).append(period)
    return slots


@register.filter
def period_type_buckets(periods):
    """Converts periods into buckets of days of the week.

    The periods in each bucket is sorted by start time.
    """
    slots = {}
    for period in periods:
        dows = tuple(period.days_of_week)
        slots[dows[0]] = slots.get(dows[0], {})
        slots[dows[0]][dows] = slots[dows[0]].get(dows, []) + [period]
        #for dow in period.days_of_week:
        #   slots[dow] = slots.get(dow, []) + [period]
    for slot in slots.values():
        for periods in slot.values():
            periods.sort(key=lambda p: p.start)
    return slots


@register.filter
def sections_for(sections, course):
    return [s for s in sections if s.course_id == course.id]


@register.filter
def sum_credits(courses):
    min_creds = max_creds = 0
    for course in courses:
        min_creds += course.min_credits
        max_creds += course.max_credits
    if min_creds == max_creds:
        return "%d credit%s" % (min_creds, '' if min_creds == 1 else 's')
    return "%d - %d credits" % (min_creds, max_creds)


@register.filter
def seats_left(sections):
    return sum(s.seats_left for s in sections)


@register.filter
def join(collection, sep=', '):
    return unicode(sep).join(map(unicode, collection))
