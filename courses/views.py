from django.views.generic import ListView, RedirectView
from django.core.urlresolvers import reverse
from timetable.courses import models

class SelectedCoursesMixin(object):
	def get_selected_courses(self):
		year, month = self.kwargs['year'], self.kwargs['month']
		course_ids = self.request.session.get('selected', [])
		return models.Course.objects.filter_by_semester(year, month).filter(id__in=course_ids)

	def get_context_data(self, **kwargs):
		data = super(SelectedCoursesMixin, self).get_context_data(**kwargs)
		data['selected_courses'] = self.get_selected_courses()
		return data

class DepartmentListView(SelectedCoursesMixin, ListView):
	"Provides all departments."
	context_object_name = 'departments'

	def get_queryset(self):
		year, month = self.kwargs['year'], self.kwargs['month']
		return models.Department.objects.filter_by_semester(year, month).distinct().order_by('code')

class RedirectToLatestSemesterRedirectView(RedirectView):
	"Simply redirects to the latest semester."
	url_name = 'course-finder'

	def get_url_name(self):
		return self.url_name

	def get_redirect_url(self, **kwargs):
		semester = models.Semester.objects.all().order_by('-year', '-month')[0]
		return reverse(self.url_name, kwargs=dict(year=semester.year, month=semester.month))
