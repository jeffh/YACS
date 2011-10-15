from django import template

register = template.Library()

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
def seats_left_for_course(course, sections=None):
	if sections is None:
		sections = course.sections.all()
	else:
		sections = [s for s in sections if course.id == s.course_id]

	seats_left = 0
	for section in sections:
		seats_left += section.seats_left

	return seats_left

@register.filter
def join(collection, sep=','):
	return unicode(sep).join(map(unicode, collection))
