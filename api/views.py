import mimetypes
import plistlib
import xmlrpclib

from django.views.generic import ListView, DetailView
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from django.conf import settings

from yacs.courses import models, views
from yacs.courses.utils import ObjectJSONEncoder


# add some mimetypes
mimetypes.add_type('application/x-plist', 'plist')
mimetypes.add_type('application/x-binary-plist', 'bplist')
mimetypes.add_type('application/x-binary-plist', 'biplist')


SHOW_QUERIES = getattr(settings, 'API_RETURN_QUERIES', False) and settings.DEBUG


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
        if SHOW_QUERIES:
            from django.db import connection
            json['$DEBUG'] = {
                'query_count': len(connection.queries),
                'sql': connection.queries
            }
        return json

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
            if settings.DEBUG:
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

