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
    url(r'^composer/%s$' % uuid_match, views.composer, name='hindustani-composer'),
    url(r'^artist/%s$' % uuid_match, views.artist, name='hindustani-artist'),
    url(r'^release/%s$' % uuid_match, views.release, name='hindustani-release'),
    url(r'^recording/%s$' % uuid_match, views.recording, name='hindustani-recording'),
    url(r'^work/%s$' % uuid_match, views.work, name='hindustani-work'),
    url(r'^raag/(?P<raagid>\d+)$', views.raag, name='hindustani-raag'),
    url(r'^taal/(?P<taalid>\d+)$', views.taal, name='hindustani-taal'),
    url(r'^laay/(?P<laayid>\d+)$', views.laay, name='hindustani-laay'),
    url(r'^form/(?P<formid>\d+)$', views.form, name='hindustani-form'),
    url(r'^instrument/(?P<instrumentid>\d+)$', views.instrument, name='hindustani-instrument'),
)
