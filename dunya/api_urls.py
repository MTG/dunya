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

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
external_identifier = r'(?P<external_identifier>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^carnatic/raaga$', api.RaagaList.as_view(), name='api-carnatic-raaga-list'),
    url(r'^carnatic/taala$', api.TaalaList.as_view(), name='api-carnatic-taala-list'),
    url(r'^carnatic/instrument$', api.InstrumentList.as_view(), name='api-carnatic-instrument-list'),
    url(r'^carnatic/work$', api.WorkList.as_view(), name='api-carnatic-work-list'),
    url(r'^carnatic/recording$', api.RecordingList.as_view(), name='api-carnatic-recording-list'),
    url(r'^carnatic/artist$', api.ArtistList.as_view(), name='api-carnatic-artist-list'),
    url(r'^carnatic/concert$', api.ConcertList.as_view(), name='api-carnatic-concert-list'),
)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

