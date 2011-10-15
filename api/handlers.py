from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import throttle, rc
from yacs.courses import models as courses
from yacs.scheduler import models
from yacs.scheduler.scheduler import compute_schedules


class ReadAPIBaseHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, version):
        return self.model.objects.all()

class PeriodHandler(ReadAPIBaseHandler):
    model = courses.Period

    def read(self, request, version, pid=None):
        qs = self.model.objects.all()

        if pid:
            return qs.get(pk=pid)

        return qs

class DepartmentHandler(ReadAPIBaseHandler):
    model = courses.Department

    def read(self, request, version, year=None, month=None, code=None):
        qs = self.model.objects.by_semester(year, month).distinct()

        if code:
            return qs.get(code=code)

        return qs

class SemesterHandler(ReadAPIBaseHandler):
    model = courses.Semester
    fields = ('id', 'date_updated', 'month', 'name', 'year', 'num_of_departments', 'num_of_courses', 'num_of_sections')

    def read(self, request, version, year=None, month=None):
        qs = self.model.objects.all()

        if year:
            qs = qs.filter(year=year)

        if month:
            qs = qs.filter(month=month)

        if year and month:
            instance = qs.get()
            instance.num_of_departments = instance.departments.count()
            instance.num_of_courses = instance.courses.count()
            instance.num_of_sections = instance.sections.count()
            return instance

        return qs

class BulkCourseHandler(ReadAPIBaseHandler):
    model = courses.Course
    fields = ('id', 'name', 'min_credits', 'max_credits', 'number')

    def read(self, request, version, code=None, number=None, year=None, month=None, name=None, crns=None):
        qs = self.model.objects.by_semester(year, month)

        # filter by CRNs
        if request.GET.get('crns'):
            qs = qs.filter(section__crn__in=set(request.GET.getlist('crns')))

        # filter by department

        if code:
            qs = qs.filter(department__code=code)

        if number:
            qs = qs.filter(number=number)

        # filter by name

        if name:
            qs = qs.filter(name__icontains=name)

        return qs.distinct()

class CourseHandler(BulkCourseHandler):
    model = courses.Course
    fields = (
        'id', 'name', 'min_credits', 'max_credits', 'number', 'grade_type',
        ('department', ('code', 'name')),
        ('sections_for_semester', ('crn', 'number', 'seats_taken', 'seats_total')),
        ('semesters', ('year', 'month', 'name'))
    )

    def read(self, request, version, cid=None, **kwargs):
        qs = super(CourseHandler, self).read(request, version, **kwargs).select_related()
        try:
            semester_obj = courses.Semester.objects.get(year=kwargs['year'], month=kwargs['month'])
        except:
            return rc.NOT_FOUND
        if cid:
            qs = qs.filter(id=cid)

        try:
            obj = qs.get()
        except self.model.DoesNotExist:
            return rc.NOT_FOUND

        obj.sections_for_semester = obj.sections.filter(semesters=semester_obj)
        return obj

class SectionHandler(ReadAPIBaseHandler):
    model = courses.Section
    fields = (
        'id', 'number', 'crn', 'seats_taken', 'seats_total',
        ('section_times_for_semester', ('kind', 'location', 'instructor', ('period', ('start', 'end', 'days_of_week')))),
        ('course', ('id', 'name')),
    )

    def read(self, request, version, cid=None, number=None, crn=None, year=None, month=None):
        qs = self.model.objects.by_semester(year, month)

        if cid is not None:
            qs = qs.filter(course__id=cid)

        if number is not None:
            qs = qs.filter(number=number)

        if crn is not None:
            qs = qs.filter(crn=crn)

        if not (cid or number or crn):
            return rc.BAD_REQUEST

        objects = []
        for section in qs.select_related().distinct():
            section.section_times_for_semester = section.section_times.filter(
                semester__year__contains=year, semester__month__contains=month
            )
            objects.append(section)
        return objects

class ScheduleHandler(AnonymousBaseHandler):
    model = courses.Course
    allowed_methods = ('GET',)

    @throttle(20, timeout=60) # 20 requests per 60 seconds
    def read(self, request, version, year, month):
        # requires CRNs or Course IDs
        GET, GET_LIST = request.GET.get, request.GET.getlist

        if not (GET('crns') or GET('cids')):
            response = rc.BAD_REQUEST
            response.write(': all params are empty.')
            return response

        crns, cids = GET_LIST('crns'), GET_LIST('cids')
        verbose = GET('complete', 0)

        semester = courses.Semester.objects.get(year=year, month=month)

        if crns:
            crns = self.coerce_to_ints(crns)
            self.assert_size_restriction(crns)
            schedules = models.Schedule.objects.get_or_create_all_from_crns(crns, semester)
            return self.output_schedules(schedules, verbose)
        if cids:
            cids = self.coerce_to_ints(cids)
            self.assert_size_restriction(cids)
            schedules = models.Schedule.objects.get_or_create_all_from_course_ids(cids, semester)
            return self.output_schedules(schedules, verbose)

        return []

    def coerce_to_ints(self, items):
        try:
            return [int(x) for x in items]
        except (TypeError, ValueError):
            raise rc.BAD_REQUEST

    def assert_size_restriction(self, items):
        if len(items) > 7:
            response = rc.BAD_REQUEST
            response.write('Too many courses specified.')
            raise response

    def output_schedules(self, schedules, verbose=False):
        output = [schedule.to_dict() for schedule in schedules]
        if verbose:
            output = {
                'schedules': output,
                'sections': self.sections_for_schedules(schedules),
                'courses': self.courses_for_schedules(schedules),
            }
        return output

    def sections_for_schedules(self, schedules):
        result = {}
        for schedule in schedules:
            for section in schedule.sections.all():
                result[section.crn] = section
        return result

    def courses_for_schedules(self, schedules):
        result = {}
        for schedule in schedules:
            for course in schedule.courses.all():
                result[course.id] = course
        return result


class OldScheduleHandler(AnonymousBaseHandler):
    model = courses.Course
    allowed_methods = ('GET',)

    @throttle(10, timeout=60) # restrict creating schedules to 10 request every 60 seconds
    def read(self, request, version, year, month):
        # requires CRNs or Course IDs
        GET, GET_LIST = request.GET.get, request.GET.getlist

        if not (GET('crns') or GET('cids')):
            response = rc.BAD_REQUEST
            response.write(': all params are empty.')
            return response

        crns, cids = GET_LIST('crns'), GET_LIST('cids')
        verbose = GET('complete', 0)

        if crns:
            crns = self._coerce_to_ints(crns)
            self._assert_size_restriction(crns)
            return self._compute_schedules(self._read_crns(request, crns, year, month), verbose)
        if cids:
            cids = self._coerce_to_ints(cids)
            self._assert_size_restriction(cids)
            return self._compute_schedules(self._read_courses(request, cids, year, month), verbose)
        return []

    def _coerce_to_ints(self, items):
        try:
            return [int(x) for x in items]
        except (TypeError, ValueError):
            raise rc.BAD_REQUEST

    def _assert_size_restriction(self, items):
        if len(items) > 7:
            response = rc.BAD_REQUEST
            response.write('Too many courses specified.')
            raise response

    def _compute_schedules(self, selected_courses, verbose=True):
        output = []
        if verbose:
            output = {
                'schedules': [],
                'sections': {},
                'courses': {}
            }
        for schedule in selected_courses:
            s = {}
            for course, section in schedule.items():
                ref = course.id
                if verbose:
                    output['courses'][ref] = course
                    output['sections'][section.crn] = section
                s[ref] = section.crn
            if verbose:
                output['schedules'].append(s)
            else:
                output.append(s)

        return output

    def _read_courses(self, request, course_ids, year, month):
        selected_courses = courses.Course.objects.filter(
            id__in=course_ids, semesters__year__contains=year, semesters__month__contains=month
        )

        return compute_schedules(selected_courses)

    def _read_crns(self, request, crns, year, month):
        sections = courses.Section.objects.filter(
            crn__in=crns, semesters__year__contains=year, semesters__month__contains=month
        ).select_related('course').distinct()

        return self._process_sections(sections)

    def _process_sections(self, queryset):
        selected_courses = {}
        for section in queryset:
            selected_courses[section.course] = selected_courses.get(section.course, []) + [section]

        return compute_schedules(selected_courses)

