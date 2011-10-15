from django.views.generic import ListView, RedirectView, DetailView, View
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.db.models import Q
from yacs.courses import models
from json import dumps

import re

SELECTED_COURSES_SESSION_KEY = 'selected'

def get_sections(courses, year, month):
    course_ids = [c.id for c in courses]
    queryset = models.Section.objects.by_semester(year, month)
    sections = queryset.filter(course__id__in=course_ids)

    return sections

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
        return self.kwargs['year'], self.kwargs['month']

    def get_context_data(self, **kwargs):
        data = super(SemesterBasedMixin, self).get_context_data(**kwargs)
        data['sem_year'], data['sem_month'] = self.get_year_and_month()
        return data

class SelectedCoursesMixin(SemesterBasedMixin):
    def get_selected_courses(self):
        year, month = self.get_year_and_month()
        course_ids = self.request.session.get(SELECTED_COURSES_SESSION_KEY, [])
        queryset = models.Course.objects.by_semester(year, month)
        courses = queryset.filter(id__in=course_ids).select_related('department')

        return courses, get_sections(courses, year, month)

    def get_context_data(self, **kwargs):
        data = super(SelectedCoursesMixin, self).get_context_data(**kwargs)
        data['selected_courses'], data['selected_sections'] = self.get_selected_courses()
        return data

class SelectedCoursesListView(SelectedCoursesMixin, ListView):
    template_name = 'courses/selected_courses_list.html'

    def get_queryset(self):
        return self.get_selected_courses()[1]

    def get_context_data(self, **kwargs):
        data = super(SelectedCoursesListView, self).get_context_data(**kwargs)
        return data

class DepartmentListView(SelectedCoursesMixin, ListView):
    "Provides all departments."
    context_object_name = 'departments'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        return models.Department.objects.by_semester(year, month)

class SearchMixin(object):

    def get_context_data(self, **kwargs):
        data = super(SearchMixin, self).get_context_data(**kwargs)
        data['departments'] = models.Department.objects.all()
        return data

class SearchCoursesListView(SearchMixin, SelectedCoursesMixin, ListView):
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'

    def get_queryset(self):
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
        return courses.full_select(year, month)

    def get_context_data(self, **kwargs):
        data = super(SearchCoursesListView, self).get_context_data(**kwargs)
        data['query'] = self.request.GET.get('q', '')
        data['query_department'] = self.request.GET.get('d', 'all')
        data['department'] = self.department
        data['search_results'] = True
        data['sections'] = get_sections(data['courses'], *self.get_year_and_month())
        return data

class CourseByDeptListView(SearchMixin, SelectedCoursesMixin, ListView):
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        self.department = models.Department.objects.get(code=self.kwargs['code'])
        courses = models.Course.objects.by_semester(year, month).by_department(self.department)

        query = self.request.GET.get('q')
        if query:
            courses = courses.search(query, self.department)
        return courses.select_related('department').full_select(year, month)

    def get_context_data(self, **kwargs):
        data = super(CourseByDeptListView, self).get_context_data(**kwargs)
        data['department'] = self.department
        data['query'] = self.request.GET.get('q', '')
        data['sections'] = get_sections(data['courses'], *self.get_year_and_month())
        return data

class CourseDetailView(SemesterBasedMixin, DetailView):
    "Shows gruesome amount of detail for a course"
    context_object_name = 'course'

    def get_query_set(self):
        return models.Course.objects.all().select_related()

    def get_object(self):
        deptcode, number = self.kwargs.get('code'), self.kwargs.get('number')
        obj = self.get_query_set().get(department__code=deptcode, number=number)

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

class RedirectToLatestSemesterRedirectView(RedirectView):
    "Simply redirects to the latest semester."
    url_name = 'departments'

    def get_url_name(self):
        return self.url_name

    def get_redirect_url(self, **kwargs):
        semester = models.Semester.objects.all().order_by('-year', '-month')[0]
        return reverse(self.url_name, kwargs=dict(year=semester.year, month=semester.month))

class DeselectCoursesView(SemesterBasedMixin, View):
    def get_redirect_url(self):
        redirect_url = self.request.POST.get('redirect_to')
        if redirect_url:
            year, month = self.get_year_and_month()
            return redirect(redirect_url, year=year, month=month)
        return redirect('index')

    def render_to_response(self, context):
        return self.get_redirect_url()

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
        selection = request.session[SELECTED_COURSES_SESSION_KEY] = self.update_selected()
        return self.render_to_response(self.get_context_data(selection=selection))

class SelectCoursesView(DeselectCoursesView):
    def update_selected(self):
        if type(self.request.session.get(SELECTED_COURSES_SESSION_KEY, {})) != dict:
            self.request.session[SELECTED_COURSES_SESSION_KEY] = {}

        year, month = self.get_year_and_month()
        course_ids = self.request.session.get(SELECTED_COURSES_SESSION_KEY, {})
        PREFIX = 'course_'

        for name in self.request.POST:
            if not name.startswith(PREFIX):
                continue
            try:
                cid = int(name[len(PREFIX):])
            except (ValueError, TypeError):
                raise HttpResponseBadRequest("Hey, what do you think you're trying to do?")
            # TODO: optimize queries
            section_ids = list(models.Section.objects.filter(
                course__id=cid, semesters__year__contains=year, semesters__month__contains=month
            ).values_list('crn', flat=True))
            course_ids[cid] = section_ids

        return course_ids

