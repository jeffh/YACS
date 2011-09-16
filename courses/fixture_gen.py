from fixture_generator import fixture_generator
from timetable.courses import models
import datetime

def now():
	return datetime.datetime.now()

def create(model, *rows, **apply_to_all):
	for r in rows:
		model.objects.get_or_create(**r, **apply_to_all)

@fixture_generator(models.Department]):
def generate_departments():
	create(models.Department,
		dict(name='Architecture', code='ARCH'),
		dict(name='Congnitive Science', code='COGSCI'),
		dict(name='Computer Science', code='CSCI'),
		dict(name='Electrical, Computer and Systems Engineering', code='ECSE'),
		dict(name='Information Technology', code='IT'),
		dict(name='Mechanical, Aerospace & Nuclear Engineering', code='MANE'),
		college=models.College.objects.all()[0]
	)

@fixture_generator(models.Semester)
def generate_semesters():
	create(models.Semester,
		dict(year=2010, month=1, name='Spring 2010', ref='201001.xml', date_updated=now()),
		dict(year=2010, month=5, name='Summer 2010', ref='201005.xml', date_updated=now()),
		dict(year=2010, month=9, name='Fall 2010', ref='201009.xml', date_updated=now()),
		dict(year=2011, month=1, name='Spring 2011', ref='201001.xml', date_updated=now()),
		dict(year=2011, month=5, name='Summer 2011', ref='201005.xml', date_updated=now()),
		dict(year=2011, month=9, name='Fall 2011', ref='201009.xml', date_updated=now()),
		college=models.College.objects.all()[0]
	)

@fixture_generator(models.Course, models.OfferedFor, requires=['generate_departments'])
def generate_courses():
	create(models.Course,
		# TODO
		college=models.College.objects.all()[0],
		department=models.Department.objects.get(code='CSCI')
	)

#@fixture_generator(requires=[])
#def generate_all():
#	pass