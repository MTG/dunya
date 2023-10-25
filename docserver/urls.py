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

from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from docserver import views

uuid_match = r'(?P<uuid>[a-f0-9-:]+)'
external_identifier = r'(?P<external_identifier>[a-f0-9-:]+)'
# Some external identifiers are combinations of two uuids separated by a :, so we allow more values than a strict uuid

api_patterns = [
    path('collections', views.CollectionList.as_view(), name='collection-list'),
    re_path(fr'by-id/{external_identifier}/(?:add|update)/(?P<file_type>[a-z0-9-]+)', views.SourceFile.as_view(), name='ds-add-sourcetype'),
    path('by-id/<uuid:uuid>/<slug:ftype>', views.download_external, name='ds-download-external'),
    re_path(fr'by-id/{uuid_match}\.(?P<ftype>mp3)', views.download_external, name='ds-download-mp3'),
    path('by-id/<str:external_identifier>', views.DocumentDetail.as_view(), name='ds-document-external'),
    path('<slug:slug>', views.CollectionDetail.as_view(), name='collection-detail'),
    path('<slug:slug>/<str:external_identifier>', views.DocumentDetail.as_view(), name='ds-document')
]
api_patterns = format_suffix_patterns(api_patterns, allowed=['json', 'api'])

urlpatterns = [
    path('', views.index),
    # Essentia management
    path('manager/addmodule', views.addmodule, name='docserver-addmodule'),
    path('manager/<type>/<slug:slug>/<int:version>', views.collectionversion, name='docserver-collectionversion'),
    path('manager/delete_collection/<slug:slug>', views.delete_collection, name='docserver-delete-collection'),
    path('manager/delete-derived-files/<slug:slug>/<int:moduleversion>', views.delete_derived_files, name='docserver-delete-derived-files'),
    path('manager/addcollection', views.addcollection, name='docserver-addcollection'),
    path('manager/collection/<slug:slug>/files', views.collectionfiles, name='docserver-collectionfiles'),
    path('manager/collection/<slug:slug>', views.collection, name='docserver-collection'),
    path('manager/collection/<slug:slug>/edit', views.editcollection, name='docserver-editcollection'),
    path('manager/addfiletype', views.addfiletype, name='docserver-addfiletype'),
    path('manager/filetypes', views.filetypes, name='docserver-filetypes'),
    path('manager/filetype/<slug:slug>', views.filetype, name='docserver-filetype'),
    path('manager/filetype/<slug:slug>/edit', views.editfiletype, name='docserver-editfiletype'),
    path('manager/collection/<slug:slug>/<uuid:uuid>', views.file, name='docserver-file'),
    path('manager/collection/<slug:slug>/<uuid:uuid>/<int:version>', views.file, name='docserver-file'),
    path('manager/module/<int:module>', views.module, name='docserver-module'),
    path('manager/worker/<slug:hostname>', views.worker, name='docserver-worke'),
    path('manager/workers', views.workers_status, name='docserver-workers'),
    path('manager/modules', views.modules_status, name='docserver-modules'),
    path('manager/', views.manager, name='docserver-manager'),
] + api_patterns
