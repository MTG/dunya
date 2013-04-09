from django.conf.urls import patterns, url

from carnatic import views

urlpatterns = patterns('',
    url(r'^$', views.main, name='carnatic-main'),
    url(r'^overview$', views.overview, name='carnatic-overview'),
    url(r'^composer/(?P<composerid>\d+)$', views.composer, name='carnatic-composer'),
    url(r'^artist/(?P<artistid>\d+)$', views.artist, name='carnatic-artist'),
    url(r'^concert/(?P<concertid>\d+)$', views.concert, name='carnatic-concert'),
    url(r'^recording/(?P<recordingid>\d+)$', views.recording, name='carnatic-recording'),
    url(r'^work/(?P<workid>\d+)$', views.work, name='carnatic-work'),
    url(r'^raaga/(?P<raagaid>\d+)$', views.raaga, name='carnatic-raaga'),
    url(r'^taala/(?P<taalaid>\d+)$', views.taala, name='carnatic-taala'),
    url(r'^instrument/(?P<instrumentid>\d+)$', views.instrument, name='carnatic-instrument'),
)
