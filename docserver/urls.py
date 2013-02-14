from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from docserver import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', 'api_root'),
    url(r'^collections$', views.CollectionList.as_view(), name='collection-list'),
    url(r'^(?P<cslug>[^/]+)$', views.CollectionDetail.as_view(), name='collection-detail'),
    url(r'^(?P<cslug>[^/]+)/%s$' % uuid_match, views.DocumentDetail.as_view(), name='ds-document'),
    url(r'^(?P<cslug>[^/]+)/%s/(?P<ftype>[a-z0-9]+)$' % uuid_match, views.download, name='ds-download')
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
