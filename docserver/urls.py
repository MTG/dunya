from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from docserver import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
external_identifier = r'(?P<external_identifier>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^collections$', views.CollectionList.as_view(), name='collection-list'),
    url(r'^by-external/%s/(?P<ftype>[a-z0-9]+)$' % uuid_match, views.download_external, name='ds-download-external'),
    url(r'^by-external/%s$' % external_identifier, views.DocumentDetailExternal.as_view(), name='ds-document-external'),
    url(r'^(?P<slug>[^/]+)$', views.CollectionDetail.as_view(), name='collection-detail'),
    url(r'^(?P<slug>[^/]+)/(?P<pk>\d)$', views.DocumentDetail.as_view(), name='ds-document'),
    url(r'^(?P<slug>[^/]+)/(?P<pk>\d)/(?P<ftype>[a-z0-9]+)$', views.download, name='ds-download'),

    # Essentia management
    url(r'manager/addessentia/', views.addessentia, name='docserver-addessentia'),
    url(r'manager/addmodule', views.addmodule, name='docserver-addmodule'),
    url(r'manager/module', views.module, name='docserver-module'),
    url(r'manager/', views.manager, name='docserver-manager'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
