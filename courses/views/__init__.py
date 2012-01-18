import re

from django.views.generic import ListView, RedirectView, DetailView, View
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from yacs.courses import models
from yacs.courses.utils import ObjectJSONEncoder, DAYS
from yacs.courses.views.mixins import (SemesterBasedMixin, AjaxJsonResponseMixin, SelectedCoursesMixin,
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


class SelectedCoursesListView(AjaxJsonResponseMixin, SelectedCoursesMixin, ListView):
    "Lists all user selected courses & sections."
    template_name = 'courses/selected_courses_list.html'

    def convert_context_to_json(self, context):
        "Returns the user's selection as JSON."
        return self.json_encoder.encode(self.get_user_selection())

    def get_queryset(self):
        return []  # perform no db operations, see convert_context_to_json()


class DepartmentListView(SelectedCoursesMixin, ListView):
    "List all departments for a particular semester."
    context_object_name = 'departments'
    fetch_semester = True

    def get_queryset(self):
        return self.filter_by_semester(models.Department.objects.all())


class SearchCoursesListView(PartialResponseMixin, SearchMixin, SelectedCoursesMixin, ListView):
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

        courses = self.filter_by_semester(models.Course.objects.all()).select_related()
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
        data['sections'] = self.get_sections(data['courses'], *self.get_year_and_month())
        return data


class CourseByDeptListView(SearchMixin, SelectedCoursesMixin, ListView):
    "Shows all courses for a given department."
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'
    fetch_semester = True

    # optional parameters used by newapi
    def get_queryset(self, prefetch_department=True, full_select=True):
        self.department = get_object_or_404(models.Department, code=self.kwargs['code'])
        courses = self.filter_by_semester(models.Course.objects.all()).by_department(self.department)

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
        return qs

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
        "Fetches all sections for a given course."
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
    "Performs the operation of deselecting courses. This is also used by javascript to update the selected courses."
    def get_redirect_url(self):
        "Returns the URL to redirect to after this view completes its work."
        redirect_url = self.request.POST.get('redirect_to')
        if redirect_url:
            year, month = self.get_year_and_month()
            return redirect(redirect_url, year=year, month=month)
        return redirect('index')

    def render_to_response(self, context):
        "Perform the redirect unless this is an ajax request."
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


    # we only accept POST requests
    def post(self, request, *args, **kwargs):
        self.request, self.args, self.kwargs = request, args, kwargs
        selection = self.update_selected()
        request.session[SELECTED_COURSES_SESSION_KEY] = selection
        return self.render_to_response(self.get_context_data(selection=selection))


class SelectCoursesView(DeselectCoursesView):
    "Selects a given course. This is used for non-javascript clients."
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

