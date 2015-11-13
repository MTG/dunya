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

from dashboard import views
from dashboard import statistic_views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^$', views.index, name='dashboard-home'),
    url(r'^collection/%s/change$' % (uuid_match, ), views.edit_access_collections, name='dashboard-access-collections-edit'),
    url(r'^collection/list$', views.list_access_collections, name='dashboard-access-collections-list'),
    url(r'^collection/%s$' % (uuid_match, ), views.collection, name='dashboard-collection'),
    url(r'^collection/%s/edit$' % (uuid_match, ), views.editcollection, name='dashboard-editcollection'),
    url(r'^delete_collection/%s$' % (uuid_match, ), views.delete_collection, name='dashboard-delete-collection'),
    url(r'^delete_collection_db_files/%s$' % (uuid_match, ), views.delete_database_files, name='dashboard-delete-collection-db-files'),
    url(r'addcollection$', views.addcollection, name='dashboard-addcollection'),
    url(r'release/(?P<releaseid>\d+)$', views.release, name='dashboard-release'),
    url(r'directory/(?P<dirid>\d+)$', views.directory, name='dashboard-directory'),
    url(r'file/(?P<fileid>\d+)$', views.file, name='dashboard-file'),
    url(r'accounts$', views.accounts, name='dashboard-accounts'),

    url(r'carnatic/coverart/', statistic_views.carnatic_coverart, name='dashboard-carnatic-coverart'),
    url(r'carnatic/releases/', statistic_views.carnatic_releases, name='dashboard-carnatic-releases'),
    url(r'carnatic/artists/', statistic_views.carnatic_artists, name='dashboard-carnatic-artists'),
    url(r'carnatic/recordings/', statistic_views.carnatic_recordings, name='dashboard-carnatic-recordings'),
    url(r'carnatic/raagataala/', statistic_views.carnatic_raagataala, name='dashboard-carnatic-raagataala'),
    url(r'carnatic/works/', statistic_views.carnatic_works, name='dashboard-carnatic-works'),
    url(r'carnatic/thillana/', statistic_views.carnatic_thillanas, name='dashboard-carnatic-thillanas'),
    url(r'carnatic/workraagataala/', statistic_views.carnatic_workraagataala, name='dashboard-carnatic-workraagataala'),
    url(r'carnatic/artists-list/', views.carnatic_artists_list, name='dashboard-carnatic-artists'),
    url(r'carnatic/artist/(?P<artistid>\d+)$', views.carnatic_artist_desc, name='dashboard-carnatic-artist'),

    url(r'carnatic/data/raagas', views.carnatic_raagas, name='dashboard-carnatic-raagas'),
    url(r'carnatic/data/taalas', views.carnatic_taalas, name='dashboard-carnatic-taalas'),
    url(r'carnatic/data/instruments', views.carnatic_instruments, name='dashboard-carnatic-instruments'),
    url(r'carnatic/data/forms', views.carnatic_forms, name='dashboard-carnatic-forms'),

    url(r'carnatic/', statistic_views.carnatic_stats, name='dashboard-carnatic-stats'),


    url(r'hindustani/coverart/', statistic_views.hindustani_coverart, name='dashboard-hindustani-coverart'),
    url(r'hindustani/releases/', statistic_views.hindustani_releases, name='dashboard-hindustani-releases'),
    url(r'hindustani/artists/', statistic_views.hindustani_artists, name='dashboard-hindustani-artists'),
    url(r'hindustani/recordings/', statistic_views.hindustani_recordings, name='dashboard-hindustani-recordings'),
    url(r'hindustani/raagataala/', statistic_views.hindustani_raagtaal, name='dashboard-hindustani-raagtaal'),
    url(r'hindustani/works/', statistic_views.hindustani_works, name='dashboard-hindustani-works'),
    url(r'hindustani/artists-list/', views.hindustani_artists_list, name='dashboard-hindustani-artists'),
    url(r'hindustani/artist/(?P<artistid>\d+)$', views.hindustani_artist_desc, name='dashboard-hindustani-artist'),

    url(r'hindustani/data/raags', views.hindustani_raags, name='dashboard-hindustani-raags'),
    url(r'hindustani/data/taals', views.hindustani_taals, name='dashboard-hindustani-taals'),
    url(r'hindustani/data/layas', views.hindustani_layas, name='dashboard-hindustani-layas'),
    url(r'hindustani/data/forms', views.hindustani_forms, name='dashboard-hindustani-forms'),
    url(r'hindustani/data/instruments', views.hindustani_instruments, name='dashboard-hindustani-instruments'),

    url(r'hindustani/', statistic_views.hindustani_stats, name='dashboard-hindustani-stats'),

    url(r'makam/data/makams', views.makam_makams, name='dashboard-makam-makams'),
    url(r'makam/data/usuls', views.makam_usuls, name='dashboard-makam-usuls'),
    url(r'makam/data/forms', views.makam_forms, name='dashboard-makam-forms'),
    url(r'makam/data/instruments', views.makam_instruments, name='dashboard-makam-instruments'),
    url(r'makam/data/symbtr/%s' % uuid_match, views.makam_symbtr, name='dashboard-makam-symbtr'),
    url(r'makam/data/symbtr/new', views.makam_symbtr, name='dashboard-makam-symbtrnew'),
    url(r'makam/data/symbtr', views.makam_symbtrlist, name='dashboard-makam-symbtrlist'),

    url(r'makam/tags', statistic_views.makam_tags, name='dashboard-makam-tags'),
    url(r'makam/recordings', statistic_views.makam_recordings, name='dashboard-makam-recordings'),
    url(r'makam/works', statistic_views.makam_works, name='dashboard-makam-works'),
    url(r'makam/artists', statistic_views.makam_artists, name='dashboard-makam-artists'),
    url(r'makam/instruments', statistic_views.makam_missing_instruments, name='dashboard-makam-missing-instruments'),

    url(r'makam/', statistic_views.makam_stats, name='dashboard-makam-stats'),
    url(r'beijing/', statistic_views.beijing_stats, name='dashboard-beijing-stats'),
    url(r'arabandalusian/$', statistic_views.andalusian_stats, name='dashboard-andalusian-stats'),
    url(r'arabandalusian/file', views.import_andalusian_elements, name='dashboard-andalusian-elements'),
    url(r'arabandalusian/catalog', views.import_andalusian_catalog, name='dashboard-andalusian-catalog'),
]
