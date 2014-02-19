from django.conf.urls import patterns, url

from makam import views

urlpatterns = patterns('',
    url(r'^$', views.main, name='makam-main'),
    url(r'^composer/%s$' % uuid_match, views.composer, name='makam-composer'),
    url(r'^artist/%s$' % uuid_match, views.artist, name='makam-artist'),
    url(r'^release/%s$' % uuid_match, views.concert, name='makam-release'),
    url(r'^recording/%s$' % uuid_match, views.recording, name='makam-recording'),
    url(r'^work/%s$' % uuid_match, views.work, name='makam-work'),
    url(r'^makam/(?P<makamid>\d+)$', views.makam, name='makam-makam'),
    url(r'^usul/(?P<usulid>\d+)$', views.usul, name='makam-usul'),
    url(r'^form/(?P<formid>\d+)$', views.form, name='makam-form'),
    url(r'^instrument/(?P<instrumentid>\d+)$', views.instrument, name='makam-instrument'),
)

