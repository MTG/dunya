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

import andalusian.api

urlpatterns = [
    path(r'orchestra', andalusian.api.OrchestraList.as_view(), name='api-andalusian-raaga-list'),
    path(r'orchestra', andalusian.api.OrchestraList.as_view(), name='api-andalusian-raaga-list'),
    path(r'orchestra/<uuid:mbid>', andalusian.api.OrchestraDetail.as_view(), name='api-andalusian-raaga-detail'),

    path(r'artist', andalusian.api.ArtistList.as_view(), name='api-andalusian-taala-list'),
    path(r'artist/<uuid:mbid>', andalusian.api.ArtistDetail.as_view(), name='api-andalusian-taala-detail'),

    path(r'album', andalusian.api.AlbumList.as_view(), name='api-andalusian-instrument-list'),
    path(r'album/<uuid:mbid>', andalusian.api.AlbumDetail.as_view(), name='api-andalusian-instrument-detail'),

    path(r'work', andalusian.api.WorkList.as_view(), name='api-andalusian-work-list'),
    path(r'work/<uuid:mbid>', andalusian.api.WorkDetail.as_view(), name='api-andalusian-work-detail'),

    path(r'genre', andalusian.api.GenreList.as_view(), name='api-andalusian-genre-list'),
    path(r'genre/<int:pk>', andalusian.api.GenreDetail.as_view(), name='api-andalusian-genre-detail'),

    path(r'recording', andalusian.api.RecordingList.as_view(), name='api-andalusian-recording-list'),
    path(r'recording/<uuid:mbid>', andalusian.api.RecordingDetail.as_view(), name='api-andalusian-recording-detail'),
    path(r'recording/<uuid:mbid>/lyric', andalusian.api.LyricDetail.as_view(), name='api-andalusian-lyric-detail'),

    path(r'instrument', andalusian.api.InstrumentList.as_view(), name='api-andalusian-instrument-list'),
    path(r'instrument/<uuid:mbid>', andalusian.api.InstrumentDetail.as_view(), name='api-andalusian-instrument-detail'),

    path(r'tab', andalusian.api.TabList.as_view(), name='api-andalusian-tab-list'),
    path(r'tab/<uuid:uuid>', andalusian.api.TabDetail.as_view(), name='api-andalusian-tab-detail'),

    path(r'mizan', andalusian.api.MizanList.as_view(), name='api-andalusian-mizan-list'),
    path(r'mizan/<uuid:uuid>', andalusian.api.MizanDetail.as_view(), name='api-andalusian-mizan-detail'),

    path(r'nawba', andalusian.api.NawbaList.as_view(), name='api-andalusian-nawba-list'),
    path(r'nawba/<uuid:uuid>', andalusian.api.NawbaDetail.as_view(), name='api-andalusian-nawba-detail'),

    path(r'form', andalusian.api.FormList.as_view(), name='api-andalusian-form-list'),
    path(r'form/<uuid:uuid>', andalusian.api.FormDetail.as_view(), name='api-andalusian-form-detail'),

    path(r'sanaa', andalusian.api.SanaaList.as_view(), name='api-andalusian-sanaa-list'),
    path(r'sanaa/<int:pk>', andalusian.api.SanaaDetail.as_view(), name='api-andalusian-sanaa-detail'),

    path(r'poem', andalusian.api.PoemList.as_view(), name='api-andalusian-poem-list'),
    path(r'poem/<int:pk>', andalusian.api.PoemDetail.as_view(), name='api-andalusian-poem-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
