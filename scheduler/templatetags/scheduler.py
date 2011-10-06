from django import template

register = template.Library()

@register.filter
def enumerate(iterable):
    i = 1
    for item in iterable:
        yield i, item
        i += 1

@register.filter
def for_dayofweek(section, dayofweek):
	if not section:
		return None
	for sp in section.all_section_periods:
		if dayofweek in sp.period.days_of_week:
			return section
	return None

@register.filter
def for_hour(section, hour):
	if not section:
		return None
	for sp in section.all_section_periods:
		if hour == sp.period.start.hour:
			return sp
	return None

@register.filter
def humanize_hour(hour):
	apm = 'am'
	if hour == 0:
		hour = 12
	if hour >= 12:
		apm = 'pm'
	if hour > 12:
		hour = hour - 12
	return "%d %s" % (hour, apm)

def seconds(time):
    return time.hour * 3600 + time.minute * 60 + time.second

@register.filter
def period_height(period, max_height='60'):
    time = seconds(period.end) - seconds(period.start)
    #return 25 # 30 min time block
    #return 41.666666667 # 50 min time block
    return time / 3600.0 * int(max_height)

def remove_zero_prefix(timestr):
    if timestr[0] == '0':
        return timestr[1:]
    return timestr

@register.filter
def normal_time(time):
    return remove_zero_prefix(time.strftime('%I:%M'))

# too much code here... may get cut
@register.filter
def display_period(period):
    format = "%s-%s"
    if period.start.strftime('%p') == period.end.strftime('%p'):
        return format % (
            remove_zero_prefix(period.start.strftime('%I:%M')),
            remove_zero_prefix(period.end.strftime('%I:%M %p')),
        )
    return format % (
        remove_zero_prefix(period.start.strftime('%I:%M %p')),
        remove_zero_prefix(period.end.strftime('%I:%M %p')),
    )




