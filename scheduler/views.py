from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

def schedules(request, year, month):
    computed_schedules = []
    return render_to_response('scheduler/schedules.html', {
        'schedules': computed_schedules,
    }, context_instance=RequestContext(request))
