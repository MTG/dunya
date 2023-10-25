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

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

import carnatic.api

urlpatterns = [
    path('raaga', carnatic.api.RaagaList.as_view(), name='api-carnatic-raaga-list'),
    path('raaga/<uuid:uuid>', carnatic.api.RaagaDetail.as_view(), name='api-carnatic-raaga-detail'),

    path('taala', carnatic.api.TaalaList.as_view(), name='api-carnatic-taala-list'),
    path('taala/<uuid:uuid>', carnatic.api.TaalaDetail.as_view(), name='api-carnatic-taala-detail'),

    path('instrument', carnatic.api.InstrumentList.as_view(), name='api-carnatic-instrument-list'),
    path('instrument/<int:pk>', carnatic.api.InstrumentDetail.as_view(), name='api-carnatic-instrument-detail'),

    path('work', carnatic.api.WorkList.as_view(), name='api-carnatic-work-list'),
    path('work/<uuid:uuid>', carnatic.api.WorkDetail.as_view(), name='api-carnatic-work-detail'),

    path('recording', carnatic.api.RecordingList.as_view(), name='api-carnatic-recording-list'),
    path('recording/<uuid:uuid>', carnatic.api.RecordingDetail.as_view(), name='api-carnatic-recording-detail'),

    path('artist', carnatic.api.ArtistList.as_view(), name='api-carnatic-artist-list'),
    path('artist/<uuid:uuid>', carnatic.api.ArtistDetail.as_view(), name='api-carnatic-artist-detail'),

    path('concert', carnatic.api.ConcertList.as_view(), name='api-carnatic-concert-list'),
    path('concert/<uuid:uuid>', carnatic.api.ConcertDetail.as_view(), name='api-carnatic-concert-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
