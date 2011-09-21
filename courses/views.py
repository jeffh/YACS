from django.views.generic import ListView, RedirectView
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from timetable.courses import models

SELECTED_COURSES_SESSION_KEY = 'selected'

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
        return queryset.filter(id__in=course_ids).select_related('department')

    def get_context_data(self, **kwargs):
        data = super(SelectedCoursesMixin, self).get_context_data(**kwargs)
        data['selected_courses'] = self.get_selected_courses()
        return data

class DepartmentListView(SelectedCoursesMixin, ListView):
    "Provides all departments."
    context_object_name = 'departments'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        return models.Department.objects.filter_by_semester(year, month).order_by('code')

class CourseByDeptListView(SelectedCoursesMixin, ListView):
    context_object_name = 'courses'

    def get_queryset(self):
        year, month = self.get_year_and_month()
        self.department = models.Department.objects.get(code=self.kwargs['code'])
        return models.Course.objects.filter_by_semester(year, month).filter(department=self.department)

    def get_context_data(self, **kwargs):
        data = super(CourseByDeptListView, self).get_context_data(**kwargs)
        data['department'] = self.department
        return data

class RedirectToLatestSemesterRedirectView(RedirectView):
    "Simply redirects to the latest semester."
    url_name = 'departments'

    def get_url_name(self):
        return self.url_name

    def get_redirect_url(self, **kwargs):
        semester = models.Semester.objects.all().order_by('-year', '-month')[0]
        return reverse(self.url_name, kwargs=dict(year=semester.year, month=semester.month))

def select_courses(request, year, month):

    if request.method == 'GET':
        return HttpResponseBadRequest("Nothing here, move along.")

    should_deselect = request.GET.get('deselect')

    redirect_url = request.POST.get('redirect_to')
    course_ids = request.session.get(SELECTED_COURSES_SESSION_KEY, [])
    PREFIX = 'course_'
    if should_deselect:
        PREFIX = 'selected_course_'

    for name in request.POST:
        if not name.startswith(PREFIX):
            continue
        try:
            cid = int(name[len(PREFIX):])
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Hey, what do you think you're trying to do.")
        if should_deselect:
            if cid in course_ids:
                course_ids.remove(cid)
        else:
            if cid not in course_ids:
                course_ids.append(cid)
    
    while len(course_ids) > 20:
        course_ids.pop(0)

    request.session[SELECTED_COURSES_SESSION_KEY] = course_ids

    print course_ids
    
    if redirect_url:
        return redirect(redirect_url, year=year, month=month)
    return redirect('index')

