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
from django.views.generic import TemplateView, RedirectView

from makam import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
title_match = r'(?:/(?P<title>[\w-]+))?'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='makam/index.html'), name='makam-main'),
    url(r'^search$', views.recordings_search, name='makam-search'),
    url(r'^info$', TemplateView.as_view(template_name="makam/info.html"), name='makam-info'),
    url(r'^stats$', TemplateView.as_view(template_name='makam/stats.html'), name='makam-stats'),
    # Keep this redirect for external links
    url(r'^overview$', RedirectView.as_view(pattern_name='makam-info', permanent=True)),
    url(r'^results-stats$', TemplateView.as_view(template_name='makam/results_stats.html'), name='makam-res-stats'),
    url(r'^recording/(?P<recordingid>\d+)%s$' % (title_match, ), views.recordingbyid, name='makam-recordingbyid'),
    url(r'^recording/%s%s$' % (uuid_match, title_match), views.recording, name='makam-recording'),
    url(r'^download-files/%s%s$' % (uuid_match, title_match),
        views.download_derived_files, name='makam-download-derived'),
    url(r'^lyric-align/%s%s$' % (uuid_match, title_match), views.lyric_alignment, name='makam-lyric-alignment'),
    url(r'^symbtr/%s$' % (uuid_match, ), views.symbtr, name='makam-symbtr'),

    url(r'^searchcomplete$', views.searchcomplete, name='makam-searchcomplete'),
    url(r'filters.json$', views.filters, name='makam-filters'),
]
