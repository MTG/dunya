# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
# 
# This file is part of Dunya
# 
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from django.conf.urls import patterns, url

from carnatic import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', views.main, name='carnatic-main'),
    url(r'^searchcomplete$', views.searchcomplete, name='carnatic-searchcomplete'),
    url(r'^composer/(?P<composerid>\d+)$', views.composerbyid, name='carnatic-composerbyid'),
    url(r'^composer/%s$' % uuid_match, views.composer, name='carnatic-composer'),
    url(r'^artist/search$', views.artistsearch, name='carnatic-artist-search'),
    url(r'^artist/(?P<artistid>\d+)$', views.artistbyid, name='carnatic-artistbyid'),
    url(r'^artist/%s$' % uuid_match, views.artist, name='carnatic-artist'),
    url(r'^concert/search$', views.concertsearch, name='carnatic-concert-search'),
    url(r'^concert/(?P<concertid>\d+)$', views.concertbyid, name='carnatic-concertbyid'),
    url(r'^concert/%s$' % uuid_match, views.concert, name='carnatic-concert'),
    url(r'^recording/(?P<recordingid>\d+)$', views.recordingbyid, name='carnatic-recordingbyid'),
    url(r'^recording/%s$' % uuid_match, views.recording, name='carnatic-recording'),
    url(r'^work/(?P<workid>\d+)$', views.workbyid, name='carnatic-workbyid'),
    url(r'^work/%s$' % uuid_match, views.work, name='carnatic-work'),
    url(r'^work/search$', views.worksearch, name='carnatic-work-search'),
    url(r'^raaga/(?P<raagaid>\d+)$', views.raaga, name='carnatic-raaga'),
    url(r'^raaga/search$', views.raagasearch, name='carnatic-raaga-search'),
    url(r'^taala/(?P<taalaid>\d+)$', views.taala, name='carnatic-taala'),
    url(r'^taala/search$', views.taalasearch, name='carnatic-taala-search'),
    url(r'^instrument/(?P<instrumentid>\d+)$', views.instrument, name='carnatic-instrument'),
    url(r'^instrument/search$', views.instrumentsearch, name='carnatic-instrument-search'),
)
