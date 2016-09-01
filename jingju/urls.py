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

from jingju import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
name_match = r'(?:/(?P<name>[\w-]+))?'
title_match = r'(?:/(?P<title>[\w-]+))?'

urlpatterns = [
    url(r'^$', views.main, name='jingju-main'),
    url(r'^recording/%s$' % uuid_match, views.recording,
        name='jingju-recording'),
    url(r'^basic-lyric-align/%s%s$' % (uuid_match, title_match),
            views.basic_lyric_alignment, name='jingju-basic-lyric-alignment'),
    ]
