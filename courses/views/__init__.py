import re

from django.views.generic import ListView, RedirectView, DetailView, View, TemplateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from courses import models
from courses.views.mixins import (SemesterBasedMixin, AjaxJsonResponseMixin,
        PartialResponseMixin, SearchMixin, SELECTED_COURSES_SESSION_KEY)


class SemesterListView(ListView):
    "Displays a list of semesters to be selected."
    def get_queryset(self):
        "Returns all semesters. Optionally can be filtered by the year."
        qs = models.Semester.objects.all()
        year = self.kwargs.get('year')
        if year:
            qs = qs.filter(year=year)
        return qs


class SemesterDetailView(SemesterBasedMixin, DetailView):
    "Displays a specific semester."
    def get_object(self):
        "Returns a specific semester, given year and month."
        return self.get_semester()


class SelectedCoursesListView(SemesterBasedMixin, TemplateView):
    "Lists all user selected courses & sections."
    template_name = 'courses/selected_courses_list.html'
    fetch_semester = True

    def get_context_data(self, **kwargs):
        year, month = self.get_year_and_month()
        context = super(SelectedCoursesListView, self).get_context_data(**kwargs)
        context['departments'] = models.Department.objects.by_semester(year, month)
        return context


class DepartmentListView(SemesterBasedMixin, ListView):
    "List all departments for a particular semester."
    context_object_name = 'departments'
    fetch_semester = True

    def get_queryset(self):
        return self.optionally_by_semester(models.Department.objects.all())


class SearchCoursesListView(PartialResponseMixin, SearchMixin, SemesterBasedMixin, ListView):
    "Show search results from a given query."
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'
    # returns HTML partials. See PartialResponseMixin
    partial_template_name = 'courses/_course_list.html'

    # optional parameters used by newapi
    def get_queryset(self, full_select=True):
        query = self.request.GET.get('q', '')
        depart = self.request.GET.get('d', 'all')
        if depart == 'all':
            depart = None

        self.department = None
        if depart:
            self.department = models.Department.objects.get(code=depart)

        courses = self.optionally_by_semester(
                models.Course.objects.all().select_related())
        courses = courses.search(query, self.department)
        if not query:
            courses = courses.order_by('department__code', 'number')
        if full_select:
            year, month = self.get_year_and_month()
            courses = courses.full_select(year, month)
        return courses

    def get_context_data(self, **kwargs):
        data = super(SearchCoursesListView, self).get_context_data(**kwargs)
        data['query'] = self.request.GET.get('q', '')
        data['query_department'] = self.request.GET.get('d', 'all')
        data['department'] = self.department
        data['search_results'] = True
        #data['sections'] = self.get_sections(data['courses'], *self.get_year_and_month())
        return data


class CourseByDeptListView(SearchMixin, SemesterBasedMixin, ListView):
    "Shows all courses for a given department."
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'
    fetch_semester = True

    # optional parameters used by api
    def get_queryset(self, prefetch_department=True, full_select=True):
        self.department = get_object_or_404(models.Department, code=self.kwargs['code'])
        courses = self.optionally_by_semester(
            models.Course.objects.all().by_department(self.department))

        query = self.request.GET.get('q')
        if query:
            courses = courses.search(query, self.department)
        if prefetch_department:
            courses = courses.select_related('department')
        if full_select:
            year, month = self.get_year_and_month()
            courses = courses.full_select(year, month)
        return courses

    def get_context_data(self, **kwargs):
        data = super(CourseByDeptListView, self).get_context_data(**kwargs)
        data['department'] = self.department
        data['query'] = self.request.GET.get('q', '')
        #data['sections'] = self.get_sections(data['courses'], *self.get_year_and_month())
        return data


class CourseDetailView(SemesterBasedMixin, DetailView):
    "Shows gruesome amount of detail for a course"
    context_object_name = 'course'

    def get_queryset(self, select_related=True):
        qs = models.Course.objects.all()
        if select_related:
            qs = qs.select_related()

        deptcode, number = self.kwargs.get('code'), self.kwargs.get('number')
        if deptcode and number:
            qs = qs.filter(department__code=deptcode, number=number)
        else:
            qs = qs.filter(id=self.kwargs.get('cid'))

        return qs

    def get_object(self):
        # attach additional properties:
        #self.apply_sections(obj)
        year, month = self.get_year_and_month()

        return self.get_queryset() \
                .select_related('department') \
                .full_select(year, month, amount=1)[0]

class RedirectToLatestSemesterRedirectView(SemesterBasedMixin, RedirectView):
    "Simply redirects to the latest semester."
    url_name = 'departments'

    def get_url_name(self):
        return self.url_name

    def get_redirect_url(self, **kwargs):
        semester = self.get_semester()
        return reverse(self.url_name, kwargs=dict(year=semester.year, month=semester.month))

