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

from jingju import views

urlpatterns = [
    path('', views.main, name='jingju-main'),
    path('recording/<uuid:uuid>', views.recording, name='jingju-recording'),
    path('basic-lyric-align/<uuid:uuid>', views.basic_lyric_alignment, name='jingju-basic-lyric-alignment'),
    path('basic-lyric-align/<uuid:uuid>/<slug:title>', views.basic_lyric_alignment, name='jingju-basic-lyric-alignment'),
    ]
