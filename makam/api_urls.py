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

import makam.api

urlpatterns = [
    path("fuzzy", makam.api.fuzzy, name="api-makam-makam-detailbyfuzzy"),
    path("form", makam.api.FormList.as_view(), name="api-makam-form-list"),
    path("form/<uuid:uuid>", makam.api.FormDetail.as_view(), name="api-makam-form-detail"),
    path("makam", makam.api.MakamList.as_view(), name="api-makam-makam-list"),
    path("makam/<uuid:uuid>", makam.api.MakamDetail.as_view(), name="api-makam-makam-detail"),
    path("usul", makam.api.UsulList.as_view(), name="api-makam-usul-list"),
    path("usul/<uuid:uuid>", makam.api.UsulDetail.as_view(), name="api-makam-usul-detail"),
    path("instrument", makam.api.InstrumentList.as_view(), name="api-makam-instrument-list"),
    path("instrument/<uuid:uuid>", makam.api.InstrumentDetail.as_view(), name="api-makam-instrument-detail"),
    path("work", makam.api.WorkList.as_view(), name="api-makam-work-list"),
    path("work/<uuid:uuid>", makam.api.WorkDetail.as_view(), name="api-makam-work-detail"),
    path("recording", makam.api.RecordingList.as_view(), name="api-makam-recording-list"),
    path("recording/<uuid:uuid>", makam.api.RecordingDetail.as_view(), name="api-makam-recording-detail"),
    path("artist", makam.api.ArtistList.as_view(), name="api-makam-artist-list"),
    path("artist/<uuid:uuid>", makam.api.ArtistDetail.as_view(), name="api-makam-artist-detail"),
    path("composer", makam.api.ComposerList.as_view(), name="api-makam-composer-list"),
    path("composer/<uuid:uuid>", makam.api.ComposerDetail.as_view(), name="api-makam-composer-detail"),
    path("release", makam.api.ReleaseList.as_view(), name="api-makam-release-list"),
    path("release/<uuid:uuid>", makam.api.ReleaseDetail.as_view(), name="api-makam-release-detail"),
    path("symbtr", makam.api.SymbtrList.as_view(), name="api-makam-symbtr-list"),
    path("symbtr/<uuid:uuid>", makam.api.SymbtrDetail.as_view(), name="api-makam-symbtr-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
