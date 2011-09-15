from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from timetable.courses.models import School


def schedules(request, school):
    school = get_object_or_404(School, slug=school)

    computed_schedules = []
    return render_to_response('scheduler/schedules.html', {
        'schedules': computed_schedules,
    }, context_instance=RequestContext(request))
