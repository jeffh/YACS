from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

MIN_API_SUPPORT = max(getattr(settings, 'API_MIN_VERSION', 1), 1)

def api_support(request, version):
	"Returns json to indicate if an API version is available or not."
	return render_to_response('api/support.json', {
		'version': version,
		'min_version': MIN_API_SUPPORT,
	}, RequestContext(request))