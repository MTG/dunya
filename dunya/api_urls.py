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
from rest_framework.urlpatterns import format_suffix_patterns

from carnatic import api
from hindustani import api 

mbid_match = r'(?P<mbid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^carnatic/raaga$', carnatic.api.RaagaList.as_view(), name='api-carnatic-raaga-list'),
    url(r'^carnatic/raaga/(?P<pk>\d+)$', carnatic.api.RaagaDetail.as_view(), name='api-carnatic-raaga-detail'),

    url(r'^carnatic/taala$', carnatic.api.TaalaList.as_view(), name='api-carnatic-taala-list'),
    url(r'^carnatic/taala/(?P<pk>\d+)$', carnatic.api.TaalaDetail.as_view(), name='api-carnatic-taala-detail'),

    url(r'^carnatic/instrument$', carnatic.api.InstrumentList.as_view(), name='api-carnatic-instrument-list'),
    url(r'^carnatic/instrument/(?P<pk>\d+)$', carnatic.api.InstrumentDetail.as_view(), name='api-carnatic-instrument-detail'),

    url(r'^carnatic/work$', carnatic.api.WorkList.as_view(), name='api-carnatic-work-list'),
    url(r'^carnatic/work/%s$' % mbid_match, carnatic.api.WorkDetail.as_view(), name='api-carnatic-work-detail'),

    url(r'^carnatic/recording$', carnatic.api.RecordingList.as_view(), name='api-carnatic-recording-list'),
    url(r'^carnatic/recording/%s$' % mbid_match, carnatic.api.RecordingDetail.as_view(), name='api-carnatic-recording-detail'),

    url(r'^carnatic/artist$', carnatic.api.ArtistList.as_view(), name='api-carnatic-artist-list'),
    url(r'^carnatic/artist/%s$' % mbid_match, carnatic.api.ArtistDetail.as_view(), name='api-carnatic-artist-detail'),

    url(r'^carnatic/concert$', carnatic.api.ConcertList.as_view(), name='api-carnatic-concert-list'),
    url(r'^carnatic/concert/%s$' % mbid_match, carnatic.api.ConcertDetail.as_view(), name='api-carnatic-concert-detail'),

    url(r'^hindustani/raag$', hindustani.api.RaagList.as_view(), name='api-hindustani-raag-list'),
    url(r'^hindustani/raag/(?P<pk>\d+)$', hindustani.api.RaagDetail.as_view(), name='api-hindustani-raag-detail'),
    
    url(r'^hindustani/taal$', hindustani.api.TaalList.as_view(), name='api-hindustani-taal-list'),
    url(r'^hindustani/taal/(?P<pk>\d+)$', hindustani.api.TaalDetail.as_view(), name='api-hindustani-taal-detail'),

    url(r'^hindustani/instrument$', hindustani.api.InstrumentList.as_view(), name='api-hindustani-instrument-list'),
    url(r'^hindustani/instrument/(?P<pk>\d+)$', hindustani.api.InstrumentDetail.as_view(), name='api-hindustani-instrument-detail'),

    url(r'^hindustani/work$', hindustani.api.WorkList.as_view(), name='api-hindustani-work-list'),
    url(r'^hindustani/work/%s$' % mbid_match, hindustani.api.WorkDetail.as_view(), name='api-hindustani-work-detail'),

    url(r'^hindustani/recording$', hindustani.api.RecordingList.as_view(), name='api-hindustani-recording-list'),
    url(r'^hindustani/recording/%s$' % mbid_match, hindustani.api.RecordingDetail.as_view(), name='api-hindustani-recording-detail'),

    url(r'^hindustani/artist$', hindustani.api.ArtistList.as_view(), name='api-hindustani-artist-list'),
    url(r'^hindustani/artist/%s$' % mbid_match, hindustani.api.ArtistDetail.as_view(), name='api-hindustani-artist-detail'),

    url(r'^hindustani/release$', hindustani.api.ReleaseList.as_view(), name='api-hindustani-release-list'),
    url(r'^hindustani/release/%s$' % mbid_match, hindustani.api.ReleaseDetail.as_view(), name='api-hindustani-release-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api',])

