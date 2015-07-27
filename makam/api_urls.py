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

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^fuzzy$', makam.api.fuzzy, name='api-makam-makam-detailbyfuzzy'),

    url(r'^form$', makam.api.FormList.as_view(), name='api-makam-form-list'),
    url(r'^form/(?P<pk>\d+)$', makam.api.formbyid, name='api-makam-form-detailbyid'),
    url(r'^form/%s$' % uuid_match, makam.api.FormDetail.as_view(), name='api-makam-form-detail'),

    url(r'^makam$', makam.api.MakamList.as_view(), name='api-makam-makam-list'),
    url(r'^makam/(?P<pk>\d+)$', makam.api.makambyid, name='api-makam-makam-detailbyid'),
    url(r'^makam/%s$' % uuid_match, makam.api.MakamDetail.as_view(), name='api-makam-makam-detail'),

    url(r'^usul$', makam.api.UsulList.as_view(), name='api-makam-usul-list'),
    url(r'^usul/(?P<pk>\d+)$', makam.api.usulbyid, name='api-makam-usul-detailbyid'),
    url(r'^usul/%s$' % uuid_match, makam.api.UsulDetail.as_view(), name='api-makam-usul-detail'),

    url(r'^instrument$', makam.api.InstrumentList.as_view(), name='api-makam-instrument-list'),
    url(r'^instrument/(?P<pk>\d+)$', makam.api.InstrumentDetail.as_view(), name='api-makam-instrument-detail'),

    url(r'^work$', makam.api.WorkList.as_view(), name='api-makam-work-list'),
    url(r'^work/%s$' % uuid_match, makam.api.WorkDetail.as_view(), name='api-makam-work-detail'),

    url(r'^recording$', makam.api.RecordingList.as_view(), name='api-makam-recording-list'),
    url(r'^recording/%s$' % uuid_match, makam.api.RecordingDetail.as_view(), name='api-makam-recording-detail'),

    url(r'^artist$', makam.api.ArtistList.as_view(), name='api-makam-artist-list'),
    url(r'^artist/%s$' % uuid_match, makam.api.ArtistDetail.as_view(), name='api-makam-artist-detail'),

    url(r'^composer$', makam.api.ComposerList.as_view(), name='api-makam-composer-list'),
    url(r'^composer/%s$' % uuid_match, makam.api.ComposerDetail.as_view(), name='api-makam-composer-detail'),

    url(r'^release$', makam.api.ReleaseList.as_view(), name='api-makam-release-list'),
    url(r'^release/%s$' % uuid_match, makam.api.ReleaseDetail.as_view(), name='api-makam-release-detail'),

    url(r'^symbtr$', makam.api.SymbtrList.as_view(), name='api-makam-symbtr-list'),
    url(r'^symbtr/%s$' % uuid_match, makam.api.SymbtrDetail.as_view(), name='api-makam-symbtr-detail')

]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
