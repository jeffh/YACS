import mimetypes
import plistlib
import xmlrpclib
import json

from django.views.generic import ListView, DetailView
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from django.conf import settings

from courses.utils import ObjectJSONEncoder, dict_by_attr, DAYS, int_list
from courses.views import decorators
from courses import models, views
from courses import encoder as encoders

from scheduler.models import SectionProxy, Selection, SectionConflict
from scheduler.domain import (
    ConflictCache, has_schedule, compute_schedules, period_stats
)


DEBUG = getattr(settings, 'DEBUG', False)

# add some mimetypes
mimetypes.init()
mimetypes.add_type('application/x-plist', '.plist')
mimetypes.add_type('application/x-binary-plist', '.bplist')
mimetypes.add_type('application/x-binary-plist', '.biplist')

class DataFormatter(object):
    def __init__(self, encoder=None, context_processor=None, default_content_type='application/json'):
        self.encoder = encoder or encoders.default_encoder
        self.context_processor = context_processor
        self.default_content_type = default_content_type

    def get_context_type_from_extension(self, ext):
        filetype = 'file.' + (ext or '')
        print filetype
        print mimetypes.guess_type('file.' + (ext or ''), strict=False)
        return mimetypes.guess_type('file.' + (ext or ''), strict=False)[0]

    def convert_data_to_json(self, context):
        indent = None
        if DEBUG:
            indent = 4
        return ObjectJSONEncoder(indent=indent).encode(context)

    def convert_data_to_xml(self, context):
        # TODO: check if datetime classes is handle automatically
        # TODO: make a proper xml dumper
        return xmlrpclib.dumps((context,))

    def convert_data_to_binary_plist(self, context):
        # TODO: handle datetime classes
        import biplist
        return biplist.writePlistToString(context)

    def convert_data_to_plist(self, context):
        # TODO: handle datetime classes
        return plistlib.writePlistToString(context)

    def convert_to_content_type(self, data, content_type=None):
        return {
            'application/json': self.convert_data_to_json,
            #'application/xml': self.convert_data_to_xml,
            #'text/xml': self.convert_data_to_xml,
            'application/x-plist': self.convert_data_to_plist,
            'application/x-binary-plist': self.convert_data_to_binary_plist,
        }.get(content_type)(data)

    def convert(self, data, content_type):
        converted_data = self.convert_to_content_type(data, content_type)
        return converted_data

    def convert_request(self, settings, request, *args, **kwargs):
        context = settings['context']
        if callable(self.context_processor):
            context = self.context_processor(context)
        context = self.encoder.encode(context)
        content_type = kwargs.get('ext') or self.default_content_type
        if content_type != self.default_content_type:
            content_type = self.get_context_type_from_extension(content_type)
        data = self.convert(context, content_type)
        response = HttpResponse(data, content_type=content_type)
        raise decorators.AlternativeResponse(response)


def wrap_request(render_settings, request, *args, **kwargs):
    def wrap_context(context):
        return {
            'success': True,
            'result': context,
            'version': kwargs.get('version', 4),
        }
    formatter = DataFormatter(context_processor=wrap_context)
    formatter.convert_request(render_settings, request, *args, **kwargs)

render = decorators.Renderer(posthook=wrap_request)


def paginate(query, page=1, per_page=1000):
    return query[(page - 1) * per_page:page * per_page]

def get_if_id_present(queryset, id=None):
    if id is not None:
        return queryset.get()
    else:
        return queryset

@render()
def raw_data(request, data, version=None, ext=None):
    return { 'context': data }

@render()
def semesters(request, id=None, version=None, ext=None):
    queryset = models.Semester.objects.optional_filter(
        id__in=int_list(request.GET.getlist('id')) or None,
        courses__id__in=int_list(request.GET.getlist('course_id')) or None,
        departments__id__in=int_list(request.GET.getlist('department_id')) or None,
        year=request.GET.get('year'), month=request.GET.get('month'),
        id=id,
    ).distinct()
    return { 'context': get_if_id_present(queryset, id) }

@render()
def departments(request, id=None, version=None, ext=None):
    queryset = models.Department.objects.optional_filter(
        id__in=int_list(request.GET.getlist('id')) or None,
        semesters__id__in=int_list(request.GET.getlist('semester_id')) or None,
        courses__id__in=int_list(request.GET.getlist('course_id')) or None,
        code__in=request.GET.getlist('code') or None,
        id=id,
    ).distinct()
    return { 'context': get_if_id_present(queryset, id) }

@render()
def courses(request, id=None, version=None, ext=None):
    queryset = models.Course.objects.optional_filter(
        semesters__id__in=int_list(request.GET.get('semester_id')) or None,
        department__code__in=request.GET.get('department_code') or None,
        department__id__in=int_list(request.GET.get('department_id')) or None,
        number__in=int_list(request.GET.get('number')) or None,
        id__in=int_list(request.GET.getlist('id')) or None,
        id=id,
    ).distinct()
    search_query = request.GET.get('search')
    queryset = queryset.search(search_query)
    return { 'context': get_if_id_present(queryset, id) }

@render()
def sections(request, id=None, version=None, ext=None):
    queryset = models.SectionPeriod.objects.optional_filter(
        semester__id__in=int_list(request.GET.getlist('semester_id')) or None,
        section__course__id__in=int_list(request.GET.getlist('course_id')) or None,
        section__id__in=int_list(request.GET.getlist('id')) or None,
        section__crn__in=int_list(request.GET.getlist('crn')) or None,
        section__id=id,
    ).select_related('section', 'period')
    section_periods = encoders.default_encoder.encode(queryset)
    sections = {}
    for section_period in section_periods:
        section = section_period['section']
        section = sections.get(section['id'], section)

        section.setdefault('section_times', []).append(section_period)
        # to prevent infinite recursion
        del section_period['section']

        period = section_period['period']
        del section_period['period']
        section_period.update(period)

        sections[section['id']] = section

    return { 'context': sections.values() }


@render()
def section_conflicts(request, id=None, version=None, ext=None):
    conflicts = SectionConflict.objects.by_unless_none(
        id=id,
        id__in=int_list(request.GET.getlist('id')) or None,
        crn__in=int_list(request.GET.getlist('crn')) or None,
    )
    if request.GET.get('as_crns'):
        conflicts = conflicts.values_list('section1__crn', 'section2__crn')
    else:
        conflicts = conflicts.values_list('section1__id', 'section2__id')

    mapping = {}
    for s1, s2 in conflicts:
        mapping.setdefault(s1, set()).add(s2)
        mapping.setdefault(s2, set()).add(s1)
    if id is not None:
        return {
            'context': {
                'id': int(id),
                'conflicts': list(mapping[int(id)])
            }
        }

    collection = []
    ids = set(int_list(request.GET.getlist('id')))
    for section_id, conflicts in mapping.items():
        if len(ids) > 0 and section_id not in ids:
            continue
        collection.append({
            'id': section_id,
            'conflicts': list(conflicts),
        })
    return { 'context': collection }


@render()
def schedules(request, slug=None, version=None):
    selection = None
    if slug:
        selection = Selection.objects.get(slug=slug)
        section_ids = selection.section_ids
    else:
        section_ids = int_list(request.GET.getlist('section_id'))

    created = False
    if not selection:
        selection, created = Selection.objects.get_or_create(
            section_ids=section_ids)

    sections = SectionProxy.objects.filter(id__in=section_ids) \
        .select_related('course').prefetch_periods()
    selected_courses = dict_by_attr(sections, 'course')
    conflict_cache = ConflictCache(
        SectionConflict.objects.as_dictionary([s.id for s in sections]))

    # if check flag given, return only if we have a schedule or not.
    if request.GET.get('check'):
        return { 'context': has_schedule(selected_courses, conflict_cache) }

    # check the cache
    if not created and selection.api_cache:
        print selection.api_cache
        return { 'context': json.loads(selection.api_cache) }

    schedules = compute_schedules(selected_courses, conflict_cache)
    print schedules

    periods = set(p for s in sections for p in s.get_periods())
    timerange, dow_used = period_stats(periods)

    # note: if you change this, caches will have to be updated somehow
    context = {
        'time_range': timerange,
        'schedules': schedules,
        'course_ids': list(set(
            c.id for c in selected_courses.keys())),
        'section_ids': list(set(
            s.id
                for sections in selected_courses.values()
                for s in sections
        )),
        'days_of_the_week': list(DAYS),
        'id': selection.slug
    }

    selection.api_cache = json.dumps(context)
    selection.save()

    return { 'context': context }

###########################################################################


class APIMixin(views.AjaxJsonResponseMixin):
    json_content_prefix = ''
    json_allow_callback = True
    default_content_type = 'application/json'

    def get_api_version(self):
        return self.kwargs.get('version', 3)

    def get_default_content_type(self):
        return self.default_content_type

    def convert_extension_to_content_type(self, ext):
        return mimetypes.guess_type('file.' + (ext or ''))[0]

    def get_content_type(self):
        format = self.kwargs.get('format')
        return self.convert_extension_to_content_type(format) or self.get_default_content_type()

    def get_api_payload(self):
        methods = ['get_object', 'get_queryset']
        for method in methods:
            methodinstance = getattr(self, method, None)
            if methodinstance:
                qs = methodinstance()
                try:
                    qs.force_into_json_array = (method == 'get_queryset')
                except:
                    pass
                try:
                    return qs.toJSON()
                except AttributeError:
                    return qs
        raise NotImplemented("Please override get_api_payload method.")

    def wrap_api_metadata(self, payload=None, status='OK'):
        json = {
            'status': status,
            'payload': payload,
        }
        # we need to inject debug info in-case we're not using json
        return self.inject_debug_info(json)

    def convert_context_to_xml(self, context):
        # TODO: check if datetime classes is handle automatically
        return xmlrpclib.dumps(context)

    def convert_context_to_binary_plist(self, context):
        # TODO: handle datetime classes
        import biplist
        return biplist.writePlistToString(context)

    def convert_context_to_plist(self, context):
        # TODO: handle datetime classes
        return plistlib.writePlistToString(context)

    def convert_to_content_type(self, content_type, data):
        return {
            'application/json': self.convert_context_to_json,
            'application/xml': self.convert_context_to_xml,
            'text/xml': self.convert_context_to_xml,
            'application/x-plist': self.convert_context_to_plist,
            #'application/x-binary-plist': self.convert_context_to_binary_plist,
        }.get(content_type)(data)

    def render_to_response(self, context):
        def body(*args, **kwargs):
            return self.convert_to_content_type(self.get_content_type(), self.wrap_api_metadata(*args, **kwargs))
        try:
            return HttpResponse(body(self.get_api_payload()), content_type=self.get_content_type())
        except HttpResponse as httpresp:
            return httpresp.__class__(body(status=str(httpresp)), content_type=self.get_content_type())
        except Exception as e:
            if DEBUG:
                raise
            return HttpResponseServerError(body(status='Server Error'), content_type=self.get_content_type())

    # override mixin method
    def should_filter_by_semester(self):
        return self.get_api_version() < 3

class ObjectList(APIMixin, ListView):
    def get_queryset(self):
        return []

    def get_api_payload(self):
        return self.kwargs.get('objects', ())


class DepartmentListView(APIMixin, views.DepartmentListView):
    pass


class SemesterListView(APIMixin, views.SemesterListView):
    pass


class SemesterDetailView(APIMixin, views.SemesterDetailView):
    pass


class SearchCoursesListView(APIMixin, views.SearchCoursesListView):
    def get_queryset(self):
        qs = super(SearchCoursesListView, self).get_queryset(full_select=False)
        qs.force_into_json_array = True
        return qs


class CourseByDeptListView(APIMixin, views.CourseByDeptListView):
    def get_api_payload(self):
        queryset = self.get_queryset(prefetch_department=False, full_select=False)
        json = self.department.toJSON()
        json['courses'] = queryset.toJSON()
        return json


class CourseListView(APIMixin, views.SemesterBasedMixin, ListView):
    def get_queryset(self):
        # new in ver3+: RESTful state. So we have to display all the semester
        # ids this course is associated with
        if self.get_api_version() < 3 or 'year' in self.kwargs and 'month' in self.kwargs:
            year, month = self.get_year_and_month()
            return models.Course.objects.by_semester(year, month).select_related('department')
        return models.Course.objects.select_related('department').select_semesters()


class CourseDetailView(APIMixin, views.CourseDetailView):
    def get_api_payload(self):
        obj = self.get_object()
        json = obj.toJSON()
        json['department'] = obj.department.toJSON()
        return json


class SectionListView(APIMixin, views.SemesterBasedMixin, ListView):
    def get_queryset(self):
        year, month = self.get_year_and_month()
        dept, num = self.kwargs.get('code'), self.kwargs.get('number')
        course_id = self.kwargs.get('cid')

        queryset = models.Section.objects.by_semester(year, month)
        if None not in (dept, num):
            queryset = queryset.by_course_code(dept, num)
        if course_id is not None:
            queryset = queryset.by_course_id(course_id)
        return queryset.full_select(year, month)


class SectionDetailView(APIMixin, views.SemesterBasedMixin, DetailView):
    def get_queryset(self):
        year, month = self.get_year_and_month()
        dept, num, crn, secnum = self.kwargs.get('code'), self.kwargs.get('number'), self.kwargs.get('crn'), self.kwargs.get('secnum')
        course_id = self.kwargs.get('cid')

        qs = models.Section.objects.by_semester(year, month).by_course_code(dept, num)
        if crn is not None:
            qs = qs.filter(crn=crn)
        if secnum is not None:
            if secnum == 'study-abroad':
                secnum = -1
            qs = qs.filter(number=secnum)
        if course_id is not None:
            qs = qs.by_course_id(course_id)

        return qs.full_select(year, month)

    def get_object(self):
        try:
            return self.get_queryset()[0]
        except IndexError:
            raise models.Section.DoesNotExist

