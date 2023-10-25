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

from carnatic import views

urlpatterns = [
    path(r'', views.main, name='carnatic-main'),
    path(r'info',
         TemplateView.as_view(template_name="carnatic/info.html"), name='carnatic-info'),

    path(r'searchcomplete', views.searchcomplete, name='carnatic-searchcomplete'),
    path(r'search', views.recordings_search, name='carnatic-search'),

    path(r'recording/<uuid:uuid>', views.recording, name='carnatic-recording'),
    path(r'recording/<uuid:uuid>/<slug:title>', views.recording, name='carnatic-recording'),

    path(r'filters.json', views.filters, name='carnatic-filters'),
]
