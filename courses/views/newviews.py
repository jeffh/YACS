from django.shortcuts import redirect
from django.views.generic import TemplateView

from courses import models
from courses.utils import DAYS
from courses.encoder import default_encoder
from courses.views.decorators import Renderer

render = Renderer(template_prefix='courses/')


################ VIEWS loaded by the a normal browser ###########################

class AjaxView(TemplateView):
    # template_name needs to be specified
    def get_context_data(self, **kwargs):
        context = super(AjaxView, self).get_context_data(**kwargs)
        year = context['sem_year'] = self.kwargs.get('year')
        month = context['sem_month'] = self.kwargs.get('month')
        context['semester'] = models.Semester.object.get(year=year, month=month)
        return context

@render(template_name='semester_list.html')
def semester_list(request, year=None, month=None):
    semesters = models.Semester.objects.optional_filter(year=year)
    return {
        'context': {
            'semesters': semesters
        }
    }

def redirect_to_latest_semester(request):
    semester = models.Semester.objects.all()[0]
    return redirect('departments', semester.year, semester.month)


@render(template_name='department_list.html')
def department_list(request, year=None, month=None):
    departments = models.Department.objects.optional_filter(
        semesters__year=year,
        semesters__month=month
    )
    semester = None
    if year and month:
        semester = models.Semester.objects.get(year=year, month=month)
    return {
        'context': {
            'sem_year': year,
            'sem_month': month,
            'semester': semester,
            'departments': departments,
        }
    }

@render()
def course_list_by_dept(request, code=None, year=None, month=None, is_search=False):
    query = request.GET.get('q')
    use_partial_template = request.GET.get('partial')

    semester = models.Semester.objects.get(year=year, month=month)
    courses = models.Course.objects.filter(semesters=semester)
    department = None
    if code: # filter by department if we can
        department = models.Department.objects.get(code=code, semesters=semester)
        courses = courses.by_department(department)

    if is_search: # filter by search query
        if not query:
            courses = courses.order_by('department__code', 'number')
        else:
            courses = courses.search(query)

    # full_select needs to be last (forces evaluation)
    courses = courses.select_related('department').full_select(year, month)

    template_name = 'course_list.html'
    if use_partial_template:
        template_name = '_' + template_name

    return {
        'template_name': template_name,
        'context': {
            'days_of_the_week': DAYS,
            'sem_year': semester.year,
            'sem_month': semester.month,
            'semester': semester,
            'department': department,
            'courses': courses,
        }
    }

