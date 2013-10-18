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

    url(r'carnatic/releases/', statistic_views.carnatic_releases, name='dashboard-carnatic-releases'),
    url(r'carnatic/artists/', statistic_views.carnatic_artists, name='dashboard-carnatic-artists'),
    url(r'carnatic/recordings/', statistic_views.carnatic_recordings, name='dashboard-carnatic-recordings'),
    url(r'carnatic/raagataala/', statistic_views.carnatic_raagataala, name='dashboard-carnatic-raagataala'),
    url(r'carnatic/works/', statistic_views.carnatic_works, name='dashboard-carnatic-works'),

    url(r'carnatic/', statistic_views.carnatic_stats, name='dashboard-stats-carnatic'),
    url(r'hindustani/', statistic_views.hindustani_stats, name='dashboard-stats-hindustani'),
    url(r'makam/', statistic_views.makam_stats, name='dashboard-stats-makam'),
    url(r'beijing/', statistic_views.beijing_stats, name='dashboard-stats-beijing'),
    url(r'arabandalusian/', statistic_views.andalusian_stats, name='dashboard-stats-andalusian'),

)

