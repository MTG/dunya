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

from dashboard import statistic_views
from dashboard import views

urlpatterns = [
    path('', views.index, name='dashboard-home'),
    path('headers', views.headers, name='dashboard-headers'),
    path('collection/<uuid:uuid>/change', views.edit_access_collections, name='dashboard-access-collections-edit'),
    path('collection/list', views.list_access_collections, name='dashboard-access-collections-list'),
    path('collection/<uuid:uuid>', views.collection, name='dashboard-collection'),
    path('collection/<uuid:uuid>/edit', views.editcollection, name='dashboard-editcollection'),
    path('delete_collection/<uuid:uuid>', views.delete_collection, name='dashboard-delete-collection'),
    path('delete_collection_db_files/<uuid:uuid>', views.delete_database_files, name='dashboard-delete-collection-db-files'),
    path('addcollection', views.addcollection, name='dashboard-addcollection'),
    path('release/<int:releaseid>', views.release, name='dashboard-release'),
    path('directory/<int:dirid>', views.directory, name='dashboard-directory'),
    path('file/<int:fileid>', views.file, name='dashboard-file'),
    path('accounts', views.accounts, name='dashboard-accounts'),

    path('carnatic/coverart/', statistic_views.carnatic_coverart, name='dashboard-carnatic-coverart'),
    path('carnatic/releases/', statistic_views.carnatic_releases, name='dashboard-carnatic-releases'),
    path('carnatic/artists/', statistic_views.carnatic_artists, name='dashboard-carnatic-artists'),
    path('carnatic/recordings/', statistic_views.carnatic_recordings, name='dashboard-carnatic-recordings'),
    path('carnatic/raagataala/', statistic_views.carnatic_raagataala, name='dashboard-carnatic-raagataala'),
    path('carnatic/works/', statistic_views.carnatic_works, name='dashboard-carnatic-works'),
    path('carnatic/thillana/', statistic_views.carnatic_thillanas, name='dashboard-carnatic-thillanas'),
    path('carnatic/workraagataala/', statistic_views.carnatic_workraagataala, name='dashboard-carnatic-workraagataala'),
    path('carnatic/artists-list/', views.carnatic_artists_list, name='dashboard-carnatic-artists'),
    path('carnatic/artist/<int:artistid>', views.carnatic_artist_desc, name='dashboard-carnatic-artist'),

    path('carnatic/data/raagas', views.carnatic_raagas, name='dashboard-carnatic-raagas'),
    path('carnatic/data/taalas', views.carnatic_taalas, name='dashboard-carnatic-taalas'),
    path('carnatic/data/instruments', views.carnatic_instruments, name='dashboard-carnatic-instruments'),
    path('carnatic/data/forms', views.carnatic_forms, name='dashboard-carnatic-forms'),

    path('carnatic/', statistic_views.carnatic_stats, name='dashboard-carnatic-stats'),


    path('hindustani/coverart/', statistic_views.hindustani_coverart, name='dashboard-hindustani-coverart'),
    path('hindustani/releases/', statistic_views.hindustani_releases, name='dashboard-hindustani-releases'),
    path('hindustani/artists/', statistic_views.hindustani_artists, name='dashboard-hindustani-artists'),
    path('hindustani/recordings/', statistic_views.hindustani_recordings, name='dashboard-hindustani-recordings'),
    path('hindustani/raagataala/', statistic_views.hindustani_raagtaal, name='dashboard-hindustani-raagtaal'),
    path('hindustani/works/', statistic_views.hindustani_works, name='dashboard-hindustani-works'),
    path('hindustani/artists-list/', views.hindustani_artists_list, name='dashboard-hindustani-artists'),
    path('hindustani/artist/<int:artistid>', views.hindustani_artist_desc, name='dashboard-hindustani-artist'),

    path('hindustani/data/raags', views.hindustani_raags, name='dashboard-hindustani-raags'),
    path('hindustani/data/taals', views.hindustani_taals, name='dashboard-hindustani-taals'),
    path('hindustani/data/layas', views.hindustani_layas, name='dashboard-hindustani-layas'),
    path('hindustani/data/forms', views.hindustani_forms, name='dashboard-hindustani-forms'),
    path('hindustani/data/instruments', views.hindustani_instruments, name='dashboard-hindustani-instruments'),

    path('hindustani/', statistic_views.hindustani_stats, name='dashboard-hindustani-stats'),

    path('makam/data/makams', views.makam_makams, name='dashboard-makam-makams'),
    path('makam/data/usuls', views.makam_usuls, name='dashboard-makam-usuls'),
    path('makam/data/forms', views.makam_forms, name='dashboard-makam-forms'),
    path('makam/data/instruments', views.makam_instruments, name='dashboard-makam-instruments'),
    path('makam/data/symbtr/<uuid:uuid>', views.makam_symbtr, name='dashboard-makam-symbtr'),
    path('makam/data/symbtr/new', views.makam_symbtr, name='dashboard-makam-symbtrnew'),
    path('makam/data/symbtr', views.makam_symbtrlist, name='dashboard-makam-symbtrlist'),

    path('makam/tags', statistic_views.makam_tags, name='dashboard-makam-tags'),
    path('makam/recordings', statistic_views.makam_recordings, name='dashboard-makam-recordings'),
    path('makam/works', statistic_views.makam_works, name='dashboard-makam-works'),
    path('makam/artists', statistic_views.makam_artists, name='dashboard-makam-artists'),
    path('makam/instruments', statistic_views.makam_missing_instruments, name='dashboard-makam-missing-instruments'),

    path('makam/', statistic_views.makam_stats, name='dashboard-makam-stats'),
    path('beijing/', statistic_views.beijing_stats, name='dashboard-beijing-stats'),
    path('arabandalusian/', statistic_views.andalusian_stats, name='dashboard-andalusian-stats'),
    path('arabandalusian/file', views.import_andalusian_elements, name='dashboard-andalusian-elements'),
    path('arabandalusian/score', views.import_andalusian_score, name='dashboard-andalusian-score'),
    path('arabandalusian/catalog', views.import_andalusian_catalog, name='dashboard-andalusian-catalog'),
]
