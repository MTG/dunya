from django.conf.urls import url

from motifdiscovery import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^$', views.main, name='motif-main'),
    url(r'^artists$', views.artists, name='motif-artists'),
    url(r'^artist/%s$' % uuid_match, views.artist, name='motif-artist'),
    url(r'^release/%s$' % uuid_match, views.release, name='motif-release'),
    url(r'^seeds/%s$' % uuid_match, views.seeds, name='motif-seeds'),
    url(r'^results/%s/(?P<seedid>[0-9]+)$' % uuid_match, views.results, name='motif-results'),
    url(r'^segment/(?P<segmentid>[0-9]+).mp3$', views.servesegment, name='motif-segment'),
]
