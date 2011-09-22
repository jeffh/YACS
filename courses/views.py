from django.views.generic import ListView, RedirectView
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.db.models import Q
from timetable.courses import models

import re

SELECTED_COURSES_SESSION_KEY = 'selected'

def get_sections(courses, year, month):
    course_ids = [c.id for c in courses]
    queryset = models.Section.objects.filter_by_semester(year, month)
    sections = queryset.filter(course__id__in=course_ids)

    return sections

class SemesterBasedMixin(object):
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
        queryset = models.Course.objects.filter_by_semester(year, month)
        courses = queryset.filter(id__in=course_ids).select_related('department')

        return courses, get_sections(courses, year, month)

    def get_context_data(self, **kwargs):
        data = super(SelectedCoursesMixin, self).get_context_data(**kwargs)
        data['selected_courses'], data['selected_sections'] = self.get_selected_courses()
        return data

class DepartmentListView(SelectedCoursesMixin, ListView):
    "Provides all departments."
    context_object_name = 'departments'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        return models.Department.objects.filter_by_semester(year, month)

class SearchCoursesMixin(SemesterBasedMixin):
    def search_courses_query(self, query, dept_code=None):
        """Generates a Q object that filters by department name & code; course name & number.
        """
        parts = query.split(' ')

        department_filter = Q()
        if isinstance(dept_code, models.Department):
            department_filter = Q(department=dept_code)
        elif dept_code:
            department_filter = Q(department__code=dept_code)

        def filter_types(query):
            return Q(department__name__icontains=query) | Q(department__code__icontains=query) | \
                Q(name__icontains=query) | Q(number__contains=query)
        
        complete_filters = filter_types(query)
        part_filters = Q()
        for part in parts:
            if part:
                part_filters = part_filters & filter_types(part)
        return (complete_filters | part_filters) & department_filter
    
    def get_context_data(self, **kwargs):
        data = super(SearchCoursesMixin, self).get_context_data(**kwargs)
        year, month = self.get_year_and_month()
        data['departments'] = models.Department.objects.filter_by_semester(year, month)
        return data

class SearchCoursesListView(SearchCoursesMixin, SelectedCoursesMixin, ListView):
    context_object_name = 'courses'
    template_name = 'course_list'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        query = self.request.GET.get('q', '')
        depart = self.request.GET.get('d', 'all')
        if depart == 'all':
            depart = None

        query_filters = Q()

        courses = models.Course.objects.filter_by_semester(year, month).select_related()
        courses = courses.filter(self.search_courses_query(query, depart))
        if not query:
            courses = courses.order_by('department__code', 'number')
        return courses

    def get_context_data(self, **kwargs):
        data = super(SearchCoursesListView, self).get_context_data(**kwargs)
        data['query'] = self.request.GET.get('q', '')
        data['query_department'] = self.request.GET.get('d', 'all')
        data['search_results'] = True
        data['sections'] = get_sections(data['courses'], *self.get_year_and_month())
        return data

class CourseByDeptListView(SearchCoursesMixin, SelectedCoursesMixin, ListView):
    context_object_name = 'courses'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        self.department = models.Department.objects.get(code=self.kwargs['code'])
        courses = models.Course.objects.filter_by_semester(year, month).filter(department=self.department)

        query = self.request.GET.get('q')
        if query:
            courses = courses.filter(self.search_courses_query(query, self.department))
        return courses

    def get_context_data(self, **kwargs):
        data = super(CourseByDeptListView, self).get_context_data(**kwargs)
        data['department'] = self.department
        data['query'] = self.request.GET.get('q', '')
        data['sections'] = get_sections(data['courses'], *self.get_year_and_month())
        return data

class RedirectToLatestSemesterRedirectView(RedirectView):
    "Simply redirects to the latest semester."
    url_name = 'departments'

    def get_url_name(self):
        return self.url_name

    def get_redirect_url(self, **kwargs):
        semester = models.Semester.objects.all().order_by('-year', '-month')[0]
        return reverse(self.url_name, kwargs=dict(year=semester.year, month=semester.month))

def deselect_courses(request, year, month):

    if request.method == 'GET':
        return HttpResponseBadRequest("Nothing here, move along.")

    redirect_url = request.POST.get('redirect_to')

    course_ids = {} # store sections (and in session)
    valid_cids = [] # only use CIDs that were checked

    for name in request.POST:
        match = re.match(r'selected_course_(\d+)_(\d+)', name)
        if not match:
            match = re.match(r'selected_course_(\d+)', name)
            if match:
                try:
                    cid = int(match.groups()[0])
                except (ValueError, TypeError):
                    return HttpResponseBadRequest("Hey, what do you think you're trying to do.")
                valid_cids.append(cid)
            continue
        try:
            cid, sid = match.groups()
            cid, sid = int(cid), int(sid)
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Hey, what do you think you're trying to do.")
        course_ids[cid] = course_ids.get(cid, []) + [sid]

    print course_ids, valid_cids
    
    for cid in set(course_ids.keys()) - set(valid_cids):
        del course_ids[cid]

    print course_ids

    #request.session[SELECTED_COURSES_SESSION_KEY] = course_ids
    
    if redirect_url:
        return redirect(redirect_url, year=year, month=month)
    return redirect('index')

def select_courses(request, year, month):

    if request.method == 'GET':
        return HttpResponseBadRequest("Nothing here, move along.")
    
    redirect_url = request.POST.get('redirect_to')

    if type(request.session.get(SELECTED_COURSES_SESSION_KEY, {})) != dict:
        request.session[SELECTED_COURSES_SESSION_KEY] = {}

    course_ids = request.session.get(SELECTED_COURSES_SESSION_KEY, {})
    PREFIX = 'course_'

    for name in request.POST:
        if not name.startswith(PREFIX):
            continue
        try:
            cid = int(name[len(PREFIX):])
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Hey, what do you think you're trying to do.")
        section_ids = list(models.Course.objects.get(id=cid).sections.all().values('id'))
        course_ids[cid] = course_ids.get(cid, []) + section_ids

    request.session[SELECTED_COURSES_SESSION_KEY] = course_ids
    
    if redirect_url:
        return redirect(redirect_url, year=year, month=month)
    return redirect('index')

