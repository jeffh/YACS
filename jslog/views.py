import json

from django.http import HttpResponse

from jslog import models


def dump(obj):
    return json.dumps(obj, indent=4)


def record(request):
    address, created = models.IPAddress.objects.get_or_create(
        address=request.META['REMOTE_ADDR'],
        useragent=request.META['HTTP_USER_AGENT']
    )
    models.Entry.objects.create(
        address=address,
        cookie=request.POST.get('cookie') or '',
        url=request.POST.get('url') or request.META.get('HTTP_REFERER'),
        message=request.POST.get('msg') or '',
        selection_json=dump(request.POST.get('selection')),
        localstorage_json=dump(request.POST.get('local')),
        meta=dump(dict(request.POST))
    )
    eids = [entry.id for entry in models.Entry.objects.all()[:30]]
    models.Entry.objects.exclude(id__in=eids).delete()
    return HttpResponse('ok')
