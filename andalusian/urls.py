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

from andalusian import views

urlpatterns = [
    path('',
         TemplateView.as_view(template_name="andalusian/index.html"), name='andalusian-main'),
    path('info',
         TemplateView.as_view(template_name="andalusian/info.html"), name='andalusian-info'),
    path('search', views.search, name='andalusian-search'),
    path('searchcomplete', views.searchcomplete, name='andalusian-searchcomplete'),
    path('filters.json', views.filters, name='andalusian-filters'),
    path('recording/<uuid:uuid>', views.recording, name='andalusian-recording'),
    path('recording/<uuid:uuid>/<slug:title>', views.recording, name='andalusian-recording'),
]

