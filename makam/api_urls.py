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

import makam.api

mbid_match = r'(?P<mbid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^makam/form$', makam.api.FormList.as_view(), name='api-makam-form-list'),
    url(r'^makam/form/(?P<pk>\d+)$', makam.api.FormDetail.as_view(), name='api-makam-form-detail'),

    url(r'^makam/makam$', makam.api.MakamList.as_view(), name='api-makam-makam-list'),
    url(r'^makam/makam/(?P<pk>\d+)$', makam.api.MakamDetail.as_view(), name='api-makam-makam-detail'),

    url(r'^makam/instrument$', makam.api.InstrumentList.as_view(), name='api-makam-instrument-list'),
    url(r'^makam/instrument/(?P<pk>\d+)$', makam.api.InstrumentDetail.as_view(), name='api-makam-instrument-detail'),

    url(r'^makam/work$', makam.api.WorkList.as_view(), name='api-makam-work-list'),
    url(r'^makam/work/%s$' % mbid_match, makam.api.WorkDetail.as_view(), name='api-makam-work-detail'),

    url(r'^makam/recording$', makam.api.RecordingList.as_view(), name='api-makam-recording-list'),
    url(r'^makam/recording/%s$' % mbid_match, makam.api.RecordingDetail.as_view(), name='api-makam-recording-detail'),

    url(r'^makam/artist$', makam.api.ArtistList.as_view(), name='api-makam-artist-list'),
    url(r'^makam/artist/%s$' % mbid_match, makam.api.ArtistDetail.as_view(), name='api-makam-artist-detail'),

    url(r'^makam/release$', makam.api.ReleaseList.as_view(), name='api-makam-release-list'),
    url(r'^makam/concert/%s$' % mbid_match, makam.api.ReleaseDetail.as_view(), name='api-makam-release-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
