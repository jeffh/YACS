from django.db.models import Manager, Q, F
from django.db.models.query import QuerySet
from yacs.courses.utils import dict_by_attr

# using the fancy queryset manager technique, as describe:
# http://adam.gomaa.us/blog/2009/feb/16/subclassing-django-querysets/index.html

class QuerySetManager(Manager):
    use_for_related_fields = True
    def __init__(self, queryset_class=QuerySet):
        super(QuerySetManager, self).__init__()
        self.queryset_class = queryset_class
        # this is technically a private API, we need to be certain we're overriding.
        assert hasattr(super(QuerySetManager, self), '_copy_to_model'), "Copy manager method no longer exists :("

    def get_query_set(self):
        return self.queryset_class(self.model, using=self.db)

    def _copy_to_model(self, model):
        "Fixes problems with model inheritance."
        mgr = super(QuerySetManager, self)._copy_to_model(model)
        mgr.queryset_class = self.queryset_class

    def __getattr__(self, attr):
        return getattr(self.get_query_set(), attr)

class SerializableQuerySet(QuerySet):

    # set to True to make toJSON() to always output a list
    force_into_json_array = False

    def toJSON(self):
        if len(self) == 1 and not self.force_into_json_array:
            return self[0].toJSON(self.query.related_select_cols)
        return [m.toJSON(self.query.related_select_cols) for m in self]


class SemesterBasedQuerySet(SerializableQuerySet):
    def by_semester(self, year=None, month=None):
        qs = self
        if year:
            qs = qs.filter(semesters__year__exact=year)

        if month:
            qs = qs.filter(semesters__month__exact=month)

        if year or month:
            qs = qs.distinct()

        return qs

class SectionPeriodQuerySet(SemesterBasedQuerySet):
    def by_semester(self, year=None, month=None):
        qs = self
        if year:
            qs = qs.filter(semester__year__exact=year)

        if month:
            qs = qs.filter(semester__month__exact=month)

        if year or month:
            qs = qs.distinct()

        return qs

    def by_course_code(self, code, number, year=None, month=None):
        return self.by_semester(year, month).filter(section__course__department__code=code, section__course__number=number)

    def by_course(self, course, year=None, month=None):
        return self.by_semester(year, month).filter(section__course=course)

    def by_sections(self, sections, year=None, month=None):
        return self.by_semester(year, month).filter(section__in=sections)

    def by_courses(self, courses, year=None, month=None):
        return self.by_semester(year, month).filter(section__course__in=courses)

    def select_instructors(self, course):
        return self.by_course(course).values_list('instructor', flat=True).distinct().order_by('instructor')

    def select_kinds(self, course):
        return self.by_course(course).values_list('kind', flat=True).distinct().order_by('kind')

def reverse_select_related(dict):
    params = []
    for key, value in dict.items():
        params.append(key)
        params.extend("%s__%s" % (key, x) for x in reverse_select_related(value))
    return params

class SectionQuerySet(SemesterBasedQuerySet):
    def full_select(self, year=None, month=None):
        """Returns all Sections in the given queryset, plus SectionPeriod and Periods.
        """
        select_related = tuple('section__' + x for x in reverse_select_related(self.query.select_related or {}))
        from yacs.courses.models import SectionPeriod
        queryset = SectionPeriod.objects.by_sections(self, year, month).select_related('period', 'section', *select_related)

        sid2sps = dict_by_attr(queryset, 'section.id')
        sid2periods = dict_by_attr(queryset, 'section.id', value_attrname='period')

        result = []
        for section in self:
            section.all_periods = sid2periods.get(section.id, [])
            section.all_section_periods = sid2sps.get(section.id, [])
            result.append(section)

        return result

    def by_course_code(self, code, number):
        qs = self
        if code:
            qs = qs.filter(course__department__code=code)
        if number:
            qs = qs.filter(course__number=number)
        return qs

    def by_course_id(self, course_id):
        return self.filter(course__id=course_id)

    def by_availability(self):
        "Filters out all sections that are unavailable. This means seats taken >= seats total."
        return self.filter(seats_taken__lt=F('seats_total'))

class CourseQuerySet(SemesterBasedQuerySet):
    def _filter_types(self, query):
        if not query:
            return Q()
        return Q(department__name__icontains=query) | Q(department__code__icontains=query) | \
            Q(name__icontains=query) | Q(number__contains=query) | \
            Q(sections__section_times__instructor__icontains=query)

    def full_select(self, year=None, month=None):
        """Returns all courses in the given queryset, plus Sections, Periods, and SectionPeriod data.

        Optionally can have all related data to be filtered by semester year and month.

        Since this operation performs multiple selects and merges the resulting queries, the queryset
        is actively evaluated.
        """
        from yacs.courses.models import SectionPeriod
        sps = SectionPeriod.objects.by_courses(self, year, month).select_related(
            'period', 'section', 'section__course'
        )

        # TODO: optimize into one loop
        sid2sps = dict_by_attr(sps, 'section_id')
        #sid2periods = dict_by_attr(sps, 'section_id', 'period')
        cid2sections = dict_by_attr([sp.section for sp in sps], 'course.id')
        cid2sps = dict_by_attr(sps, 'section.course.id')

        for sp in sps:
            sp.section.all_section_periods = sid2sps.get(sp.section.id, [])

        def section_key(section):
            return section.number

        result = []
        for course in self:
            course.all_sections = sorted(set(cid2sections.get(course.id, [])), key=section_key)
            course.all_section_periods = cid2sps.get(course.id, [])
            result.append(course)
        return result


    def _search_Q(self, query, dept_code=None):
        "Returns a composed set of django.db.models.Q objects for searching courses."
        from yacs.courses.models import Department
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

