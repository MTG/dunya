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
    url(r'^recording/0b5dd02b-d93e-4b44-81a3-d789f29ddb7d$', views.rec_0b5dd02b, name='jingju-rec-0b5dd02b'),
    url(r'^recording/3dcae41a-795c-4b7d-979b-1b52aa42dd3a$', views.rec_3dcae41a, name='jingju-rec-3dcae41a'),
    url(r'^recording/415d9fcc-bad8-45db-adec-01ffd04b9cec$', views.rec_415d9fcc, name='jingju-rec-415d9fcc'),
    url(r'^recording/87b5c1b2-e718-4ae7-8662-dc4ae3efd3b1$', views.rec_87b5c1b2, name='jingju-rec-87b5c1b2'),
]
