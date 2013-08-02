from django.conf.urls import patterns, url

from dashboard import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', views.index, name='dashboard-home'),
    url(r'collection/%s$' % (uuid_match, ), views.collection, name='dashboard-collection'),
    url(r'release/(?P<releaseid>\d+)$', views.release , name='dashboard-release'),
    url(r'directory/(?P<dirid>\d+)$', views.directory , name='dashboard-directory'),
    url(r'file/(?P<fileid>\d+)$', views.file , name='dashboard-file'),
)

