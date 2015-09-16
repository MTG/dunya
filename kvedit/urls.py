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

from kvedit import views

urlpatterns = [
    url(r'categories$', views.categories, name='kvedit-categories'),
    url(r'category/(?P<cat_id>\d+)$', views.items, name='kvedit-items'),
    url(r'category/(?P<cat_id>\d+)/edit/(?P<item_id>[^/]+)$', views.edit_item, name='kvedit-edit-item'),
]
