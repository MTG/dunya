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

import andalusian.api

mbid_match = r'(?P<mbid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'


urlpatterns = [
    url(r'^orchestra$', andalusian.api.OrchestraList.as_view(), name='api-andalusian-raaga-list'),
    url(r'^orchestra/%s$' % mbid_match, andalusian.api.OrchestraDetail.as_view(), name='api-andalusian-raaga-detail'),

    url(r'^artist$', andalusian.api.ArtistList.as_view(), name='api-andalusian-taala-list'),
    url(r'^artist/%s$' % mbid_match, andalusian.api.ArtistDetail.as_view(), name='api-andalusian-taala-detail'),

    url(r'^album$', andalusian.api.AlbumList.as_view(), name='api-andalusian-instrument-list'),
    url(r'^album/%s$' % mbid_match, andalusian.api.AlbumDetail.as_view(), name='api-andalusian-instrument-detail'),

    url(r'^work$', andalusian.api.WorkList.as_view(), name='api-andalusian-work-list'),
    url(r'^work/%s$' % mbid_match, andalusian.api.WorkDetail.as_view(), name='api-andalusian-work-detail'),

    url(r'^genre$', andalusian.api.GenreList.as_view(), name='api-andalusian-genre-list'),
    url(r'^genre/(?P<pk>\d+)$', andalusian.api.GenreDetail.as_view(), name='api-andalusian-genre-detail'),

    url(r'^recording$', andalusian.api.RecordingList.as_view(), name='api-andalusian-recording-list'),
    url(r'^recording/%s$' % mbid_match, andalusian.api.RecordingDetail.as_view(), name='api-andalusian-recording-detail'),
    url(r'^recording/%s/lyric$' % mbid_match, andalusian.api.LyricDetail.as_view(), name='api-andalusian-lyric-detail'),

    url(r'^instrument$', andalusian.api.InstrumentList.as_view(), name='api-andalusian-instrument-list'),
    url(r'^instrument/(?P<pk>\d+)$', andalusian.api.InstrumentDetail.as_view(), name='api-andalusian-instrument-detail'),

    url(r'^tab$', andalusian.api.TabList.as_view(), name='api-andalusian-tab-list'),
    url(r'^tab/%s$' % uuid_match, andalusian.api.TabDetail.as_view(), name='api-andalusian-tab-detail'),

    url(r'^mizan$', andalusian.api.MizanList.as_view(), name='api-andalusian-mizan-list'),
    url(r'^mizan/%s$' % uuid_match, andalusian.api.MizanDetail.as_view(), name='api-andalusian-mizan-detail'),

    url(r'^nawba$', andalusian.api.NawbaList.as_view(), name='api-andalusian-nawba-list'),
    url(r'^nawba/%s$' % uuid_match, andalusian.api.NawbaDetail.as_view(), name='api-andalusian-nawba-detail'),

    url(r'^form$', andalusian.api.FormList.as_view(), name='api-andalusian-form-list'),
    url(r'^form/%s$' % uuid_match, andalusian.api.FormDetail.as_view(), name='api-andalusian-form-detail'),

    url(r'^sanaa$', andalusian.api.SanaaList.as_view(), name='api-andalusian-sanaa-list'),
    url(r'^sanaa/(?P<pk>\d+)$', andalusian.api.SanaaDetail.as_view(), name='api-andalusian-sanaa-detail'),

    url(r'^poem$', andalusian.api.PoemList.as_view(), name='api-andalusian-poem-list'),
    url(r'^poem/(?P<pk>\d+)$', andalusian.api.PoemDetail.as_view(), name='api-andalusian-poem-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
