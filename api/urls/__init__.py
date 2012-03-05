from django.conf.urls.defaults import patterns, include, url

from api.views import raw_data

urlpatterns = patterns('',
    url(r'^$', raw_data, {
            'version': 4,
            'data': {
                'supported_versions': [2, 3, 4],
            }
        }, name='versions'),

    url(r'^4', include('api.urls.v4', namespace='v4')),
    url(r'^3/', include('api.urls.v3', namespace='v3')),
    url(r'^2/', include('api.urls.v2', namespace='v2')),
)
