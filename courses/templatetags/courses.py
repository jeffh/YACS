from django import template

from yacs.courses.utils import DAYS

register = template.Library()

@register.filter
def sort(iterable):
	return sorted(iterable)

@register.filter
def dow_short(dow):
	if isinstance(dow, list) or isinstance(dow, tuple):
		return tuple(map(dow_short, dow))
	return {
		'Monday': 'Mo',
		'Tuesday': 'Tu',
		'Wednesday': 'We',
		'Thursday': 'Th',
		'Friday': 'Fr',
		'Saturday': 'Sa',
		'Sunday': 'Su',
	}.get(dow)

@register.filter
def prepare_periods(periods):
	slots = {}
	for period in periods:
		dows = tuple(period.days_of_week)
		slots[dows[0]] = slots.get(dows[0], {})
		slots[dows[0]][dows] = slots[dows[0]].get(dows, []) + [period]
		#for dow in period.days_of_week:
		#	slots[dow] = slots.get(dow, []) + [period]
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
