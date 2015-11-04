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

from docserver import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
external_identifier = r'(?P<external_identifier>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

api_patterns = [
    url(r'^collections$', views.CollectionList.as_view(), name='collection-list'),
    url(r'^by-id/%s/(?:add|update)/(?P<file_type>[a-z0-9-]+)$' % external_identifier, views.SourceFile.as_view(), name='ds-add-sourcetype'),
    url(r'^by-id/%s/(?P<ftype>[a-z0-9-]+)$' % uuid_match, views.download_external, name='ds-download-external'),
    url(r'^by-id/%s\.(?P<ftype>mp3)$' % uuid_match, views.download_external, name='ds-download-mp3'),
    url(r'^by-id/%s$' % external_identifier, views.DocumentDetail.as_view(), name='ds-document-external'),
    url(r'^(?P<slug>[^/]+)$', views.CollectionDetail.as_view(), name='collection-detail'),
    url(r'^(?P<slug>[^/]+)/%s$' % external_identifier, views.DocumentDetail.as_view(), name='ds-document')
]
api_patterns = format_suffix_patterns(api_patterns, allowed=['json', 'api'])

urlpatterns = [
    url(r'^$', views.index),
    # Essentia management
    url(r'manager/addmodule', views.addmodule, name='docserver-addmodule'),
    url(r'manager/(?P<type>(un)?processed)/(?P<slug>[^/]+)/(?P<version>\d+)$', views.collectionversion, name='docserver-collectionversion'),
    url(r'manager/delete_collection/(?P<slug>[^/]+)$', views.delete_collection, name='docserver-delete-collection'),
    url(r'manager/addcollection$', views.addcollection, name='docserver-addcollection'),
    url(r'manager/collection/(?P<slug>[^/]+)/files$', views.collectionfiles, name='docserver-collectionfiles'),
    url(r'manager/collection/(?P<slug>[^/]+)$', views.collection, name='docserver-collection'),
    url(r'manager/collection/(?P<slug>[^/]+)/edit$', views.editcollection, name='docserver-editcollection'),
    url(r'manager/addfiletype$', views.addfiletype, name='docserver-addfiletype'),
    url(r'manager/filetypes$', views.filetypes, name='docserver-filetypes'),
    url(r'manager/filetype/(?P<slug>[^/]+)$', views.filetype, name='docserver-filetype'),
    url(r'manager/filetype/(?P<slug>[^/]+)/edit$', views.editfiletype, name='docserver-editfiletype'),
    url(r'manager/collection/(?P<slug>[^/]+)/%s(?:/(?P<version>\d+))?$' % uuid_match, views.file, name='docserver-file'),
    url(r'manager/module/(?P<module>\d+)$', views.module, name='docserver-module'),
    url(r'manager/worker/(?P<hostname>[^/]+)$', views.worker, name='docserver-worker'),
    url(r'manager/workers$', views.workers_status, name='docserver-workers'),
    url(r'manager/', views.manager, name='docserver-manager'),
] + api_patterns
