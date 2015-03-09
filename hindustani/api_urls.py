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

import hindustani.api

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^raag$', hindustani.api.RaagList.as_view(), name='api-hindustani-raag-list'),
    url(r'^raag/%s$' % (uuid_match, ), hindustani.api.RaagDetail.as_view(), name='api-hindustani-raag-detail'),

    url(r'^taal$', hindustani.api.TaalList.as_view(), name='api-hindustani-taal-list'),
    url(r'^taal/%s$' % (uuid_match, ), hindustani.api.TaalDetail.as_view(), name='api-hindustani-taal-detail'),

    url(r'^laya$', hindustani.api.LayaList.as_view(), name='api-hindustani-laya-list'),
    url(r'^laya/%s$' % (uuid_match, ), hindustani.api.LayaDetail.as_view(), name='api-hindustani-laya-detail'),

    url(r'^form$', hindustani.api.FormList.as_view(), name='api-hindustani-form-list'),
    url(r'^form/%s$' % (uuid_match, ), hindustani.api.FormDetail.as_view(), name='api-hindustani-form-detail'),

    url(r'^instrument$', hindustani.api.InstrumentList.as_view(), name='api-hindustani-instrument-list'),
    url(r'^instrument/(?P<pk>\d+)$', hindustani.api.InstrumentDetail.as_view(), name='api-hindustani-instrument-detail'),

    url(r'^work$', hindustani.api.WorkList.as_view(), name='api-hindustani-work-list'),
    url(r'^work/%s$' % uuid_match, hindustani.api.WorkDetail.as_view(), name='api-hindustani-work-detail'),

    url(r'^recording$', hindustani.api.RecordingList.as_view(), name='api-hindustani-recording-list'),
    url(r'^recording/%s$' % uuid_match, hindustani.api.RecordingDetail.as_view(), name='api-hindustani-recording-detail'),

    url(r'^artist$', hindustani.api.ArtistList.as_view(), name='api-hindustani-artist-list'),
    url(r'^artist/%s$' % uuid_match, hindustani.api.ArtistDetail.as_view(), name='api-hindustani-artist-detail'),

    url(r'^release$', hindustani.api.ReleaseList.as_view(), name='api-hindustani-release-list'),
    url(r'^release/%s$' % uuid_match, hindustani.api.ReleaseDetail.as_view(), name='api-hindustani-release-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
