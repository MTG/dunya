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

import hindustani.api

urlpatterns = [
    path('raag', hindustani.api.RaagList.as_view(), name='api-hindustani-raag-list'),
    path('raag/<int:pk>', hindustani.api.raagbyid, name='api-hindustani-raag-detailbyid'),
    path('raag/<uuid:uuid>', hindustani.api.RaagDetail.as_view(), name='api-hindustani-raag-detail'),

    path('taal', hindustani.api.TaalList.as_view(), name='api-hindustani-taal-list'),
    path('taal/<int:pk>', hindustani.api.taalbyid, name='api-hindustani-taal-detailbyid'),
    path('taal/<uuid:uuid>', hindustani.api.TaalDetail.as_view(), name='api-hindustani-taal-detail'),

    path('laya', hindustani.api.LayaList.as_view(), name='api-hindustani-laya-list'),
    path('laya/<int:pk>', hindustani.api.layabyid, name='api-hindustani-laya-detailbyid'),
    path('laya/<uuid:uuid>', hindustani.api.LayaDetail.as_view(), name='api-hindustani-laya-detail'),

    path('form', hindustani.api.FormList.as_view(), name='api-hindustani-form-list'),
    path('form/<int:pk>', hindustani.api.formbyid, name='api-hindustani-form-detailbyid'),
    path('form/<uuid:uuid>', hindustani.api.FormDetail.as_view(), name='api-hindustani-form-detail'),

    path('instrument', hindustani.api.InstrumentList.as_view(), name='api-hindustani-instrument-list'),
    path('instrument/<uuid:uuid>', hindustani.api.InstrumentDetail.as_view(), name='api-hindustani-instrument-detail'),

    path('work', hindustani.api.WorkList.as_view(), name='api-hindustani-work-list'),
    path('work/<uuid:uuid>', hindustani.api.WorkDetail.as_view(), name='api-hindustani-work-detail'),

    path('recording', hindustani.api.RecordingList.as_view(), name='api-hindustani-recording-list'),
    path('recording/<uuid:uuid>', hindustani.api.RecordingDetail.as_view(), name='api-hindustani-recording-detail'),

    path('artist', hindustani.api.ArtistList.as_view(), name='api-hindustani-artist-list'),
    path('artist/<uuid:uuid>', hindustani.api.ArtistDetail.as_view(), name='api-hindustani-artist-detail'),

    path('release', hindustani.api.ReleaseList.as_view(), name='api-hindustani-release-list'),
    path('release/<uuid:uuid>', hindustani.api.ReleaseDetail.as_view(), name='api-hindustani-release-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
