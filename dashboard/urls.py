from django.conf.urls import patterns, url

from dashboard import views
from dashboard import statistic_views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', views.index, name='dashboard-home'),
    url(r'collection/%s$' % (uuid_match, ), views.collection, name='dashboard-collection'),
    url(r'release/(?P<releaseid>\d+)$', views.release, name='dashboard-release'),
    url(r'directory/(?P<dirid>\d+)$', views.directory, name='dashboard-directory'),
    url(r'file/(?P<fileid>\d+)$', views.file, name='dashboard-file'),

    url(r'data/raagas', views.raagas, name='dashboard-raagas'),
    url(r'data/taalas', views.taalas, name='dashboard-taalas'),
    url(r'data/instruments', views.instruments, name='dashboard-instruments'),

    url(r'stats/carnatic', statistic_views.carnatic, name='dashboard-stats-carnatic'),
    url(r'stats/hindustani', statistic_views.hindustani, name='dashboard-stats-hindustani'),
    url(r'stats/makam', statistic_views.makam, name='dashboard-stats-makam'),
    url(r'stats/beijing', statistic_views.beijing, name='dashboard-stats-beijing'),
    url(r'stats/arabandalusian', statistic_views.andalusian, name='dashboard-stats-andalusian'),
)

