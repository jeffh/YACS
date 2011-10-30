from django.views.generic import ListView, RedirectView, DetailView, View
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.db.models import Q
from django.db.models.query import QuerySet
from django.conf import settings
from yacs.courses import models
from yacs.courses.utils import ObjectJSONEncoder
from json import dumps

import re

SELECTED_COURSES_SESSION_KEY = 'selected'

class AjaxJsonResponseMixin(object):
    json_content_prefix = 'for(;;); '
    json_allow_callback = False
    json_callback_parameter = 'callback'
    json_encoder = ObjectJSONEncoder(indent=4 if settings.DEBUG else None)

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content, content_type='application/json', **httpresponse_kwargs)

    def get_json_allow_callback(self):
        return self.json_allow_callback

    def get_json_callback_parameter(self):
        return self.json_callback_parameter

    def get_json_content_prefix(self):
        return self.json_content_prefix

    def get_json_callback_parameter_name(self):
        return self.request.GET.get(self.get_json_callback_parameter(), '')

    def convert_context_to_json(self, context):
        name = self.get_json_callback_parameter_name()
        obj = self.json_encoder.encode(context)
        if name:
            return "%s(%s)" % (name, obj)
        return obj

    def render_to_response(self, context):
        if self.request.is_ajax():
            return self.get_json_response(self.get_json_content_prefix() + self.convert_context_to_json(context))
        return super(AjaxJsonResponseMixin, self).render_to_response(context)

class TemplateBaseOverride(object):
    template_base = 'site_base.html'

    def get_template_base(self):
        return self.template_base

    def get_context_data(self, **kwargs):
        data = super(TemplateBaseOverride, self).get_context_data(**kwargs)
        data['template_base'] = self.get_template_base()
        return data

class SemesterBasedMixin(TemplateBaseOverride):
    def get_year_and_month(self):
        year, month = self.kwargs.get('year'), self.kwargs.get('month')
        if year or month:
            return year, month
        self.semester = getattr(self, 'semester', None) or models.Semester.objects.all().order_by('-year', '-month')[0]
        return self.semester.year, self.semester.month

    def get_semester(self):
        sem = getattr(self, 'semester', None)
        if sem is None:
            year, month = self.get_year_and_month()
            if getattr(self, 'semester', None) is None:
                self.semester = models.Semester.objects.get(year=year, month=month)
            sem = self.semester
        return sem

    def get_context_data(self, **kwargs):
        data = super(SemesterBasedMixin, self).get_context_data(**kwargs)
        data['sem_year'], data['sem_month'] = self.get_year_and_month()
        return data

class SemesterListView(ListView):
    def get_queryset(self):
        qs = models.Semester.objects.all()
        year = self.kwargs.get('year')
        if year:
            qs = qs.filter(year=year)
        return qs

class SemesterDetailView(SemesterBasedMixin, DetailView):
    def get_object(self):
        return self.get_semester()

class SelectedCoursesMixin(SemesterBasedMixin):
    def get_sections(self, courses, year, month):
        course_ids = [c.id for c in courses]
        queryset = models.Section.objects.by_semester(year, month)
        sections = queryset.filter(course__id__in=course_ids)

        return sections

    def get_selected_courses(self):
        year, month = self.get_year_and_month()
        course_ids = self.request.session.get(SELECTED_COURSES_SESSION_KEY, {})
        queryset = models.Course.objects.by_semester(year, month)
        courses = queryset.filter(id__in=course_ids.keys()).select_related('department')

        return courses, self.get_sections(courses, year, month)

    def get_selected_section_ids(self):
        return set(s for sections in self.request.session.get(SELECTED_COURSES_SESSION_KEY, {}).values() for s in sections)

    def get_context_data(self, **kwargs):
        data = super(SelectedCoursesMixin, self).get_context_data(**kwargs)
        data['selected_courses'], data['selected_course_sections'] = self.get_selected_courses()
        data['selected_section_ids'] = self.get_selected_section_ids()
        return data

class SelectedCoursesListView(AjaxJsonResponseMixin, SelectedCoursesMixin, ListView):
    template_name = 'courses/selected_courses_list.html'

    def convert_context_to_json(self, context):
        #queryset = context['selected_course_sections'].select_related('course')
        #result = self.json_encoder.encode(queryset)
        return self.json_encoder.encode(self.request.session.get(SELECTED_COURSES_SESSION_KEY, {}))

    def get_queryset(self):
        return self.get_selected_courses()[1]


class DepartmentListView(SelectedCoursesMixin, ListView):
    "Provides all departments."
    context_object_name = 'departments'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        return models.Department.objects.by_semester(year, month)

    def get_context_data(self, **kwargs):
        data = super(DepartmentListView, self).get_context_data(**kwargs)
        data['semester'] = self.get_semester()
        return data

class SearchMixin(object):

    def get_context_data(self, **kwargs):
        data = super(SearchMixin, self).get_context_data(**kwargs)
        data['departments'] = models.Department.objects.all()
        return data

class PartialResponseMixin(object):
    partial_template_name = None
    partial_parameter_name = 'partial'

    def get_partial_parameter_name(self):
        return self.partial_parameter_name

    def get_use_partial(self):
        return self.request.GET.get(self.get_partial_parameter_name())

    def get_partial_template_name(self):
        return self.partial_template_name

    def get_template_names(self):
        templates = super(PartialResponseMixin, self).get_template_names()
        if self.get_use_partial():
            templates.insert(0, self.get_partial_template_name())
        return templates

class SearchCoursesListView(PartialResponseMixin, SearchMixin, SelectedCoursesMixin, ListView):
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'
    partial_template_name = 'courses/_course_list.html'

    def get_queryset(self, full_select=True):
        year, month = self.get_year_and_month()
        query = self.request.GET.get('q', '')
        depart = self.request.GET.get('d', 'all')
        if depart == 'all':
            depart = None

        self.department = None
        if depart:
            self.department = models.Department.objects.get(code=depart)

        courses = models.Course.objects.by_semester(year, month).select_related()
        courses = courses.search(query, self.department)
        if not query:
            courses = courses.order_by('department__code', 'number')
        if full_select:
            courses = courses.full_select(year, month)
        return courses

    def get_context_data(self, **kwargs):
        data = super(SearchCoursesListView, self).get_context_data(**kwargs)
        data['query'] = self.request.GET.get('q', '')
        data['query_department'] = self.request.GET.get('d', 'all')
        data['department'] = self.department
        data['search_results'] = True
        data['sections'] = self.get_sections(data['courses'], *self.get_year_and_month())
        return data

class CourseByDeptListView(SearchMixin, SelectedCoursesMixin, ListView):
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'

    def get_queryset(self, select_related=True, full_select=True):
        year, month = self.get_year_and_month()
        self.department = models.Department.objects.get(code=self.kwargs['code'])
        courses = models.Course.objects.by_semester(year, month).by_department(self.department)

        query = self.request.GET.get('q')
        if query:
            courses = courses.search(query, self.department)
        if select_related:
            courses = courses.select_related('department')
        if full_select:
            courses = courses.full_select(year, month)
        return courses

    def get_context_data(self, **kwargs):
        data = super(CourseByDeptListView, self).get_context_data(**kwargs)
        data['department'] = self.department
        data['query'] = self.request.GET.get('q', '')
        data['sections'] = self.get_sections(data['courses'], *self.get_year_and_month())
        return data

class CourseDetailView(SemesterBasedMixin, DetailView):
    "Shows gruesome amount of detail for a course"
    context_object_name = 'course'

    def get_queryset(self):
        return models.Course.objects.all().select_related()

    def get_object(self):
        deptcode, number = self.kwargs.get('code'), self.kwargs.get('number')
        if deptcode and number:
            obj = self.get_queryset().get(department__code=deptcode, number=number)
        else:
            obj = self.get_queryset().get(id=self.kwargs.get('cid'))

        # attach additional properties:
        obj.all_sections = self.get_sections(obj)

        return obj

    def get_sections(self, course):
        year, month = self.get_year_and_month()
        section_periods = models.SectionPeriod.objects.by_course(course, year, month).select_related()

        periods_for_section = {}
        for sp in section_periods:
            periods_for_section[sp.section] = periods_for_section.get(sp.section, []) + [sp.period]

        sections = []
        for sp in section_periods:
            sp.section.all_periods = periods_for_section[sp.section]
            sections.append(sp.section)
        return sections

class RedirectToLatestSemesterRedirectView(SemesterBasedMixin, RedirectView):
    "Simply redirects to the latest semester."
    url_name = 'departments'

    def get_url_name(self):
        return self.url_name

    def get_redirect_url(self, **kwargs):
        semester = self.get_semester()
        return reverse(self.url_name, kwargs=dict(year=semester.year, month=semester.month))

class DeselectCoursesView(AjaxJsonResponseMixin, SemesterBasedMixin, View):
    def get_redirect_url(self):
        redirect_url = self.request.POST.get('redirect_to')
        if redirect_url:
            year, month = self.get_year_and_month()
            return redirect(redirect_url, year=year, month=month)
        return redirect('index')

    def render_to_response(self, context):
        if self.request.is_ajax():
            return super(DeselectCoursesView, self).render_to_response(context)
        return self.get_redirect_url()

    def convert_context_to_json(self, context):
        return self.json_encoder.encode(self.request.session[SELECTED_COURSES_SESSION_KEY])

    def get_context_data(self, **kwargs):
        return kwargs

    def update_selected(self):
        course_ids = {} # store sections (and in session)
        valid_cids = [] # only use CIDs that were checked

        for name in self.request.POST:
            match = re.match(r'selected_course_(\d+)_(\d+)', name)
            if not match:
                match = re.match(r'selected_course_(\d+)', name)
                if match:
                    try:
                        cid = int(match.groups()[0])
                    except (ValueError, TypeError):
                        raise HttpResponseBadRequest("Hey, what do you think you're trying to do?")
                    valid_cids.append(cid)
                continue
            try:
                cid, sid = match.groups()
                cid, sid = int(cid), int(sid)
            except (ValueError, TypeError):
                raise HttpResponseBadRequest("Hey, what do you think you're trying to do?")
            course_ids[cid] = course_ids.get(cid, []) + [sid]

        for cid in set(course_ids.keys()) - set(valid_cids):
            del course_ids[cid]

        return course_ids


    def post(self, request, *args, **kwargs):
        self.request, self.args, self.kwargs = request, args, kwargs
        selection = self.update_selected()
        request.session[SELECTED_COURSES_SESSION_KEY] = selection
        return self.render_to_response(self.get_context_data(selection=selection))

class SelectCoursesView(DeselectCoursesView):
    def update_selected(self):
        if not isinstance(self.request.session.get(SELECTED_COURSES_SESSION_KEY, {}), dict):
            self.request.session[SELECTED_COURSES_SESSION_KEY] = {}

        year, month = self.get_year_and_month()
        dept = self.request.POST.get('dept')
        removable_course_ids = None
        if dept:
            removable_course_ids = models.Course.objects.filter(department__code=dept).values_list('id', flat=True)

        course_ids = {}
        PREFIX = 'course_'

        for name in self.request.POST:
            if not name.startswith(PREFIX):
                continue
            try:
                cid = int(name[len(PREFIX):])
            except (ValueError, TypeError):
                raise HttpResponseBadRequest("Hey, what do you think you're trying to do?")
            # TODO: optimize queries
            section_ids = list(models.Section.objects.by_availability().
                by_course_id(cid).by_semester(year, month).values_list('crn', flat=True)
            )
            course_ids[cid] = section_ids
            if removable_course_ids is not None and cid in removable_course_ids:
                removable_course_ids.remove(cid)

        if removable_course_ids is None:
            return course_ids

        for cid, crns in self.request.session.get(SELECTED_COURSES_SESSION_KEY, {}).items():
            if cid not in course_ids and cid not in removable_course_ids:
                course_ids[cid] = crns
        return course_ids

