from django.conf.urls import patterns, url

from carnatic import views

urlpatterns = patterns('',
    url(r'^$', views.main),
    url(r'^composer/(?P<composerid>[^/])$', views.composer, name='carnatic-composer'),
    url(r'^artist/(?P<artistid>[^/])$', views.artist, name='carnatic-artist'),
    url(r'^concert/(?P<concertid>[^/])$', views.concert, name='carnatic-concert'),
    url(r'^recording/(?P<recordingid>[^/])$', views.recording, name='carnatic-recording'),
    url(r'^raaga/(?P<raagaid>[^/])$', views.raaga, name='carnatic-raaga'),
    url(r'^taala/(?P<taalaid>[^/])$', views.taala, name='carnatic-taala'),
    url(r'^instrument/(?P<instrumentid>[^/])$', views.instrument, name='carnatic-instrument'),
)
