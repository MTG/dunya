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

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

import carnatic.api

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^raaga$', carnatic.api.RaagaList.as_view(), name='api-carnatic-raaga-list'),
    url(r'^raaga/(?P<pk>\d+)$', carnatic.api.raagabyid, name='api-carnatic-raaga-detailid'),
    url(r'^raaga/%s$' % (uuid_match, ), carnatic.api.RaagaDetail.as_view(), name='api-carnatic-raaga-detail'),

    url(r'^taala$', carnatic.api.TaalaList.as_view(), name='api-carnatic-taala-list'),
    url(r'^taala/(?P<pk>\d+)$', carnatic.api.taalabyid, name='api-carnatic-taala-detailid'),
    url(r'^taala/%s$' % (uuid_match, ), carnatic.api.TaalaDetail.as_view(), name='api-carnatic-taala-detail'),

    url(r'^instrument$', carnatic.api.InstrumentList.as_view(), name='api-carnatic-instrument-list'),
    url(r'^instrument/(?P<pk>\d+)$', carnatic.api.InstrumentDetail.as_view(), name='api-carnatic-instrument-detail'),

    url(r'^work$', carnatic.api.WorkList.as_view(), name='api-carnatic-work-list'),
    url(r'^work/%s$' % uuid_match, carnatic.api.WorkDetail.as_view(), name='api-carnatic-work-detail'),

    url(r'^recording$', carnatic.api.RecordingList.as_view(), name='api-carnatic-recording-list'),
    url(r'^recording/%s$' % uuid_match, carnatic.api.RecordingDetail.as_view(), name='api-carnatic-recording-detail'),

    url(r'^artist$', carnatic.api.ArtistList.as_view(), name='api-carnatic-artist-list'),
    url(r'^artist/%s$' % uuid_match, carnatic.api.ArtistDetail.as_view(), name='api-carnatic-artist-detail'),

    url(r'^concert$', carnatic.api.ConcertList.as_view(), name='api-carnatic-concert-list'),
    url(r'^concert/%s$' % uuid_match, carnatic.api.ConcertDetail.as_view(), name='api-carnatic-concert-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
