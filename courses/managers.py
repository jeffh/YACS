from django.db.models import Manager, Q
from django.db.models.query import QuerySet
from timetable.courses.utils import dict_by_attr

class QuerySetManager(Manager):
    use_for_related_fields = True
    def __init__(self, queryset_class=QuerySet):
        super(QuerySetManager, self).__init__()
        self.queryset_class = queryset_class

    def get_query_set(self):
        return self.queryset_class(self.model, using=self.db)

    def __getattr__(self, attr):
        try:
            return super(QuerySetManager, self).__getattr__(attr)
        except AttributeError:
            return getattr(self.get_query_set(), attr)

class SemesterBasedQuerySet(QuerySet):
    def by_semester(self, year=None, month=None):
        qs = self
        if year:
            qs = qs.filter(semesters__year__contains=year)

        if month:
            qs = qs.filter(semesters__month__contains=month)

        if year or month:
            qs = qs.distinct()

        return qs

class SectionPeriodQuerySet(SemesterBasedQuerySet):
    def by_semester(self, year=None, month=None):
        qs = self
        if year:
            qs = qs.filter(semester__year__contains=year)

        if month:
            qs = qs.filter(semester__month__contains=month)

        if year or month:
            qs = qs.distinct()

        return qs

    def by_course(self, course, year=None, month=None):
        return self.by_semester(year, month).filter(section__course=course)

    def by_courses(self, courses, year=None, month=None):
        return self.by_semester(year, month).filter(section__course__in=courses)

    def select_instructors(self, course):
        return self.by_course(course).values_list('instructor', flat=True).distinct().order_by('instructor')

    def select_kinds(self, course):
        return self.by_course(course).values_list('kind', flat=True).distinct().order_by('kind')

class CourseManager(SemesterBasedQuerySet):
    def _filter_types(self, query):
        if not query:
            return Q()
        return Q(department__name__icontains=query) | Q(department__code__icontains=query) | \
            Q(name__icontains=query) | Q(number__contains=query)

    def full_select(self, year=None, month=None):
        """Returns all courses in the given queryset, plus Sections, Periods, and SectionPeriod data.

        Optionally can have all related data to be filtered by semester year and month.

        Since this operation performs multiple selects and merges the resulting queries, the queryset
        is actively evaluated.
        """
        from timetable.courses.models import SectionPeriod
        courses = self
        sps = SectionPeriod.objects.by_courses(courses, year, month).select_related(
            'period', 'section', 'section__course'
        )
        sid2sps = dict_by_attr(sps, 'section_id')
        cid2sections = dict_by_attr([sp.section for sp in sps], 'course.id')
        cid2sps = dict_by_attr(sps, 'section.course.id')

        for sp in sps:
            sp.section.all_periods = sid2sps.get(sp.section.id, [])

        result = []
        for course in courses:
            course.all_sections = cid2sections.get(course.id, [])
            course.all_section_periods = cid2sps.get(course.id, [])
            result.append(course)
        return result


    def _search_Q(self, query, dept_code=None):
        "Returns a composed set of django.db.models.Q objects for searching courses."
        from timetable.courses.models import Department
        parts = query.split(' ')

        department_filter = Q()
        if isinstance(dept_code, Department):
            department_filter = Q(department=dept_code)
        elif dept_code:
            department_filter = Q(department__code__iexact=dept_code)

        complete_filters = self._filter_types(query)
        part_filters = Q()
        for part in parts:
            if part:
                part_filters = part_filters & self._filter_types(part)
        return (complete_filters | part_filters) & department_filter

    def by_department(self, department):
        return self.filter(department=department)

    def search(self, query=None, dept=None):
        return self.filter(self._search_Q(query, dept))

