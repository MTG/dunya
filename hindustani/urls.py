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

from django.conf.urls import patterns, url

from hindustani import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', views.main, name='hindustani-main'),
    url(r'^searchcomplete$', views.searchcomplete, name='hindustani-searchcomplete'),
    url(r'^composer/%s$' % uuid_match, views.composer, name='hindustani-composer'),
    url(r'^artist/%s$' % uuid_match, views.artist, name='hindustani-artist'),
    url(r'^artist/search$', views.artistsearch, name='hindustani-artist-search'),
    url(r'^release/%s$' % uuid_match, views.release, name='hindustani-release'),
    url(r'^release/search$', views.releasesearch, name='hindustani-release-search'),
    url(r'^recording/%s$' % uuid_match, views.recording, name='hindustani-recording'),
    url(r'^work/%s$' % uuid_match, views.work, name='hindustani-work'),
    url(r'^raag/(?P<raagid>\d+)$', views.raag, name='hindustani-raag'),
    url(r'^raag/search$', views.raagsearch, name='hindustani-raag-search'),
    url(r'^taal/(?P<taalid>\d+)$', views.taal, name='hindustani-taal'),
    url(r'^taal/search$', views.taalsearch, name='hindustani-taal-search'),
    url(r'^laya/(?P<layaid>\d+)$', views.laya, name='hindustani-laya'),
    url(r'^laya/search$', views.layasearch, name='hindustani-laya-search'),
    url(r'^form/(?P<formid>\d+)$', views.form, name='hindustani-form'),
    url(r'^form/search$', views.formsearch, name='hindustani-form-search'),
    url(r'^instrument/(?P<instrumentid>\d+)$', views.instrument, name='hindustani-instrument'),
    url(r'^instrument/search$', views.instrumentsearch, name='hindustani-instrument-search'),
)
