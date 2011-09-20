MODE = 'DEVELOPMENT'

if MODE == 'STAGING':
	from timetable.settings.staging import *
elif MODE == 'PRODUCTION':
	from timetable.settings.production import *
else:
	from timetable.settings.development import *