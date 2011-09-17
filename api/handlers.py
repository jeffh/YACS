from piston.handler import BaseHandler, AnonymousBaseHandler
from timetable.courses import models as courses


class ReadAPIBaseHandler(AnonymousBaseHandler):
	allowed_methods = ('GET',)

	def read(self, request, version):
		return self.model.objects.all()


class DepartmentHandler(ReadAPIBaseHandler):
	model = courses.Department

	def read(self, request, version, year=None, month=None):
		qs = self.model.objects.all()

		if year:
			qs = qs.filter(semesters__year__contains=year).distinct()
		
		if month:
			qs = qs.filter(semesters__month__contains=month).distinct()
		
		return qs

class SemesterHandler(ReadAPIBaseHandler):
	model = courses.Semester
	exclude = ('id', 'ref',)

	def read(self, request, version, year=None, month=None):
		qs = self.model.objects.all()

		if year:
			qs = qs.filter(year=year)
		
		if month:
			qs = qs.filter(month=month)
		
		return qs

class BulkCourseHandler(ReadAPIBaseHandler):
	model = courses.Course
	fields = ('id', 'name', 'min_credits', 'max_credits', 'number')

	def read(self, request, version, code=None, number=None, year=None, month=None, name=None, crns=None):
		qs = self.model.objects.all()

		# filter by CRNs
		if request.GET.get('crns'):
			qs = qs.filter(section__crn__in=set(request.GET.getlist('crns')))

		# filter by department

		if code:
			qs = qs.filter(department__code=code)

		if number:
			qs = qs.filter(number=number)

		# filter by semester

		if year:
			qs = qs.filter(semesters__year__contains=year)
		
		if month:
			qs = qs.filter(semesters__month__contains=month)

		# filter by name

		if name:
			qs = qs.filter(name__icontains=name)
		
		return qs

class CourseHandler(BulkCourseHandler):
	model = courses.Course
	fields = (
		'id', 'name', 'min_credits', 'max_credits', 'number', 'grade_type',
		('department', ('code', 'name')),
		('sections', ('crn', 'number', 'seats_taken', 'seats_total', ('semesters', ('year', 'month')))),
		('semesters', ('year', 'month', 'name'))
	)

	def read(self, request, version, cid, **kwargs):
		qs = super(CourseHandler, self).read(request, version, **kwargs)
		return qs.select_related().get(id=cid)

class SectionHandler(ReadAPIBaseHandler):
	model = courses.Section
	fields = (
		'number', 'crn', 'seats_taken', 'seats_total',
		('semesters', ('year', 'month', 'name')),
		('periods', ('start', 'end', 'days_of_week')),
		('course', ('id', 'name')),
	)

	def read(self, request, version, cid=None, number=None, crn=None, year=None, month=None):
		qs = self.model.objects

		if year is not None:
			qs = qs.filter(semesters__year__contains=year).distinct()
		
		if month is not None:
			qs = qs.filter(semesters__month__contains=month).distinct()

		if cid is not None:
			qs = qs.filter(course__id=cid)

		if number is not None:
			qs = qs.filter(number=number)

		if crn is not None:
			qs = qs.filter(crn=crn)

		if qs == self.model.objects:
			raise ValueError("Invalid Query")
		
		return qs.select_related()

