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
from django.views.generic.base import TemplateView

from hindustani import views

urlpatterns = [
    path('', views.main, name='hindustani-main'),
    path('info',
         TemplateView.as_view(template_name='hindustani/info.html'), name='hindustani-info'),

    path('searchcomplete', views.searchcomplete, name='hindustani-searchcomplete'),
    path('search', views.recordings_search, name='hindustani-search'),
    path('recording/<int:recordingid>', views.recordingbyid, name='hindustani-recordingbyid'),
    path('recording/<uuid:uuid>', views.recording, name='hindustani-recording'),
    path('recording/<uuid:uuid>/<slug:title>', views.recording, name='hindustani-recording'),
    path('filters.json', views.filters, name='hindustani-filters'),
]
