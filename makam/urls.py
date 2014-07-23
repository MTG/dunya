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

from makam import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
name_match = r'(?:/(?P<name>[\w-]+))?'
title_match = r'(?:/(?P<title>[\w-]+))?'

urlpatterns = patterns('',
    url(r'^$', views.main, name='makam-main'),
    url(r'^composer/%s%s$' % (uuid_match, name_match), views.composer, name='makam-composer'),
    url(r'^artist/%s%s$' % (uuid_match, name_match), views.artist, name='makam-artist'),
    url(r'^release/%s%s$' % (uuid_match, title_match), views.release, name='makam-release'),
    url(r'^recording/%s%s$' % (uuid_match, title_match), views.recording, name='makam-recording'),
    url(r'^work/%s%s$' % (uuid_match, title_match), views.work, name='makam-work'),
    url(r'^makam/(?P<makamid>\d+)%s$' % (name_match, ), views.makam, name='makam-makam'),
    url(r'^usul/(?P<usulid>\d+)%s$' % (name_match, ), views.usul, name='makam-usul'),
    url(r'^form/(?P<formid>\d+)%s$' % (name_match, ), views.form, name='makam-form'),
    url(r'^instrument/(?P<instrumentid>\d+)%s$' % (name_match, ), views.instrument, name='makam-instrument'),
)

