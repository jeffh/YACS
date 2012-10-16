from django.db.models import Manager, Q, F
from django.db.models.query import QuerySet

from courses.utils import dict_by_attr


def set_prefetch_cache(model, field, cache):
    if not hasattr(model, '_prefetched_objects_cache'):
        model._prefetched_objects_cache = {}
    model._prefetched_objects_cache[field] = cache

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


class OptionalFilterMixin(object):
    def optional_filter(self, **kwargs):
        for key, value in kwargs.items():
            if value is None:
                del kwargs[key]
        return self.filter(**kwargs)


class SerializableQuerySet(OptionalFilterMixin, QuerySet):

    # set to True to make toJSON() to always output a list
    force_into_json_array = False

    def toJSON(self):
        if len(self) == 1 and not self.force_into_json_array:
            return self[0].toJSON(self.query.related_select_cols)
        return [m.toJSON(self.query.related_select_cols) for m in self]


class PublicSemestersQuerySetManager(QuerySetManager):
    def get_query_set(self):
        return super(PublicSemestersQuerySetManager, self).get_query_set().filter(visible=True)


class SemesterBasedQuerySet(SerializableQuerySet):
    YEAR_QUERY_PARAM = 'semesters__year__exact'
    MONTH_QUERY_PARAM = 'semesters__month__exact'

    def by_semester(self, year_or_sem=None, month=None):
        qs = self

        # read model
        if hasattr(year_or_sem, 'year'):
            month = year_or_sem.month
            year = year_or_sem.year
        else:
            year = year_or_sem

        if year:
            qs = qs.filter(**{self.YEAR_QUERY_PARAM: year})

        if month:
            qs = qs.filter(**{self.MONTH_QUERY_PARAM: month})

        if year or month:
            qs = qs.distinct()

        return qs


class SectionPeriodQuerySet(SemesterBasedQuerySet):
    YEAR_QUERY_PARAM = 'semester__year__exact'
    MONTH_QUERY_PARAM = 'semester__month__exact'

    def by_crns(self, crns, year=None, month=None):
        return self.by_semester(year, month).filter(crn__in=crns)

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
    YEAR_QUERY_PARAM = 'semester__year__exact'
    MONTH_QUERY_PARAM = 'semester__month__exact'

    def prefetch_periods(self):
        return self.prefetch_related('periods', 'section_times', 'section_times__period')

    def by_crns(self, crns, year=None, month=None):
        return self.by_semester(year, month).filter(crn__in=crns)

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

    def full_select(self, year=None, month=None, amount=None):
        """Returns all courses in the given queryset, plus Sections, Periods, and SectionPeriod data.

        Optionally can have all related data to be filtered by semester year and month.

        Since this operation performs multiple selects and merges the resulting queries, the queryset
        is actively evaluated.
        """
        from courses.models import SectionPeriod
        sps = SectionPeriod.objects.by_courses(self, year, month).select_related(
            'period', 'section', 'section__course__id'
        )

        # TODO: optimize into one loop
        sid2sps = dict_by_attr(sps, 'section_id')
        sid2periods = dict_by_attr(sps, 'section_id', 'period')
        cid2sections = dict_by_attr([sp.section for sp in sps], 'course.id')
        cid2sps = dict_by_attr(sps, 'section.course.id')

        for sp in sps:
            set_prefetch_cache(sp.section, 'section_times', sid2sps.get(sp.section.id, []))
            set_prefetch_cache(sp.section, 'periods', sid2periods.get(sp.section.id, []))

        def section_key(section):
            return section.number

        result = []
        courses = self
        if amount is not None:
            courses[:amount]
        for course in courses:
            sections = sorted(set(cid2sections.get(course.id, [])), key=section_key)
            for section in sections:
                section.course = course
            set_prefetch_cache(course, 'sections', sections)
            result.append(course)
        return result

    def _search_Q(self, query, dept_code=None):
        "Returns a composed set of django.db.models.Q objects for searching courses."
        from courses.models import Department
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
        return self.filter(self._search_Q(query or '', dept)).distinct()
