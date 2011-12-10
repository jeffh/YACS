from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from yacs.courses import models
from yacs.courses.utils import ObjectJSONEncoder, DAYS

SELECTED_COURSES_SESSION_KEY = 'selected'

class AjaxJsonResponseMixin(object):
    json_content_prefix = 'for(;;); '
    json_allow_callback = False
    json_callback_parameter = 'callback'
    json_encoder = ObjectJSONEncoder(indent=4 if settings.DEBUG else None)

    def get_json_response(self, content, **httpresponse_kwargs):
        "Returns the HttpResponse object for a json response."
        return HttpResponse(content, content_type='application/json', **httpresponse_kwargs)

    def get_json_allow_callback(self):
        "Returns boolean indicating if this view allows jsonp callbacks."
        return self.json_allow_callback

    def get_json_callback_parameter(self):
        "Returns the GET parameter name of the jsonp callback. This parameter is read to get the callback name."
        return self.json_callback_parameter

    def get_json_content_prefix(self):
        "Returns a string of data that should be prefixed to the JSON response. This is used to prevent XSS."
        return self.json_content_prefix

    def get_json_callback_parameter_name(self):
        """Returns the callback parameter name (string).

        The default uses get_json_callback_parameter to get the parameter name and reads the corresponding value
        in the GET request dictionary. Returns an empty string if no callback name parameter name was provided.
        """
        return self.request.GET.get(self.get_json_callback_parameter(), '')

    def convert_context_to_json(self, context):
        """Converts a given context dictionary into the JSON for output. Returns a JSON string.

        Internally uses get_json_callback_parameter_name to get a jsonp callback name if provided.
        Otherwise, simply outputs the JSON data.
        """
        name = self.get_json_callback_parameter_name()
        obj = self.json_encoder.encode(context)
        if name:
            return "%s(%s)" % (name, obj)
        return obj

    def get_is_ajax(self):
        """Returns True if the given request is an ajax request, and JSON processing should be done instead of the
        regular http request processing.

        Default operation is an alias to Django's request.is_ajax().
        """
        return self.request.is_ajax()

    def render_to_response(self, context):
        """Handles the case of returning JSON for incoming ajax requests. Otherwise uses the view's default processing
        mechanisms.

        Returns an HttpResponse object.
        """
        if self.get_is_ajax():
            return self.get_json_response(self.get_json_content_prefix() + self.convert_context_to_json(context))
        return super(AjaxJsonResponseMixin, self).render_to_response(context)

class TemplateBaseOverride(object):
    template_base = 'site_base.html'

    def get_template_base(self):
        "Returns the template base to use. Defaults to the template_base class variable."
        return self.template_base

    def get_context_data(self, **kwargs):
        "Sets `template_base` in the template context variable to be the result of get_template_base()."
        data = super(TemplateBaseOverride, self).get_context_data(**kwargs)
        data['template_base'] = self.get_template_base()
        return data

class SemesterBasedMixin(TemplateBaseOverride):
    fetch_semester = False
    def get_year_and_month(self):
        """Returns a tuple of the current semester's year and month.

        Will use the kwarg values from the URL or queries the database for the most recent semester.
        If the database is queried. The semester instance variable is set to the semester object fetched.

        This method assumes a semester object would exist in the database.
        """
        year, month = self.kwargs.get('year'), self.kwargs.get('month')
        if year or month:
            return year, month
        self.semester = getattr(self, 'semester', None) or models.Semester.objects.order_by('-year', '-month')[0]
        return self.semester.year, self.semester.month

    def get_semester(self):
        """Returns the semester object corresponding to the year and month from get_year_and_month().

        Does not perform an extra database query if get_year_and_month() already performed one (reads semester instance var).
        """
        sem = getattr(self, 'semester', None)
        if sem is None:
            year, month = self.get_year_and_month()
            if getattr(self, 'semester', None) is None:
                self.semester = get_object_or_404(models.Semester.objects, year=year, month=month)
            sem = self.semester
        return sem

    def get_context_data(self, **kwargs):
        """Sets `sem_year` and `sem_month` to the current semesters year and month.

        If fetch_semester class variable is set, then `semester` contains the semester object (uses get_semester()).
        """
        data = super(SemesterBasedMixin, self).get_context_data(**kwargs)
        data['sem_year'], data['sem_month'] = self.get_year_and_month()
        if self.fetch_semester:
            data['semester'] = self.get_semester()
        return data

class SelectedCoursesMixin(SemesterBasedMixin):
    def get_sections(self, courses, year, month):
        "Returns all sections for all course ids, given it the year and month they were offered."
        course_ids = [c.id for c in courses]
        queryset = models.Section.objects.by_semester(year, month)
        sections = queryset.filter(course__id__in=course_ids)

        return sections

    def get_user_selection(self):
        "Returns a dictionary of user selected courses (course id mapped to section crns)."
        return self.request.session.get(SELECTED_COURSES_SESSION_KEY, {})

    def get_user_selected_course_ids(self):
        "Returns a list of all course ids the user selected."
        return self.get_user_selection().keys()

    def get_user_selected_section_crns(self):
        "Returns a set of selected section CRNs."
        return set(s for sections in self.get_user_selection().values() for s in sections)

    def get_selected_courses(self, course_ids):
        "Returns the selected courses from the given set of course ids. Prefetches all corresponding section and department data."
        year, month = self.get_year_and_month()
        queryset = models.Course.objects.by_semester(year, month)
        courses = queryset.filter(id__in=course_ids).select_related('department').full_select(year, month)

        return courses

    def get_context_data(self, **kwargs):
        "Assigns `selected_courses` to the selected courses, `selected_section_ids` to all section crns, and `dow` to days of the week."
        data = super(SelectedCoursesMixin, self).get_context_data(**kwargs)
        data['selected_courses'] = self.get_selected_courses(self.get_user_selected_course_ids())
        data['selected_section_ids'] = self.get_user_selected_section_crns()
        data['dows'] = DAYS  # TODO: probably move this to its own mixin?
        return data


class SearchMixin(object):

    def get_context_data(self, **kwargs):
        "Returns all the departments for the search form."
        data = super(SearchMixin, self).get_context_data(**kwargs)
        data['departments'] = models.Department.objects.all()
        return data

class PartialResponseMixin(object):
    "Allows a view to return a template partial (instead of extending base)."
    partial_template_name = None
    partial_parameter_name = 'partial'

    def get_partial_parameter_name(self):
        "Returns the parameter name in GET to determine if the partial template should be used"
        return self.partial_parameter_name

    def get_use_partial(self):
        "Returns a boolean value indicated if the partial template should be used or not."
        return self.request.GET.get(self.get_partial_parameter_name())

    def get_partial_template_name(self):
        "Returns the partial template to use. Defaults to the partial_template_name class variable."
        return self.partial_template_name

    def get_template_names(self):
        """Returns all templates names to search for. If get_use_partial returns True, inserts the partial
        template name to use.
        """
        templates = super(PartialResponseMixin, self).get_template_names()
        if self.get_use_partial():
            templates.insert(0, self.get_partial_template_name())
        return templates
