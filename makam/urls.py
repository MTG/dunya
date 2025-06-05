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
from django.views.generic import TemplateView

from makam import views

urlpatterns = [
    path(r"", TemplateView.as_view(template_name="makam/index.html"), name="makam-main"),
    path(r"search", views.recordings_search, name="makam-search"),
    path(r"info", TemplateView.as_view(template_name="makam/info.html"), name="makam-info"),
    path(r"stats", TemplateView.as_view(template_name="makam/stats.html"), name="makam-stats"),
    path(r"overview", TemplateView.as_view(template_name="makam/overview.html"), name="makam-overview"),
    path(r"results-stats", TemplateView.as_view(template_name="makam/results_stats.html"), name="makam-res-stats"),
    path(r"recording/<uuid:uuid>", views.recording, name="makam-recording"),
    path(r"recording/<uuid:uuid>/<slug:title>", views.recording, name="makam-recording"),
    path(r"download-files/<uuid:uuid>", views.download_derived_files, name="makam-download-derived"),
    path(r"download-files/<uuid:uuid>/<slug:title>", views.download_derived_files, name="makam-download-derived"),
    path(r"lyric-align/<uuid:uuid>", views.lyric_alignment, name="makam-lyric-alignment"),
    path(r"lyric-align/<uuid:uuid>/<slug:title>", views.lyric_alignment, name="makam-lyric-alignment"),
    path(r"score/<uuid:uuid>", views.work_score, name="makam-score"),
    path(r"symbtr/<uuid:uuid>", views.symbtr, name="makam-symbtr"),
    path(r"searchcomplete", views.searchcomplete, name="makam-searchcomplete"),
    path(r"filters.json", views.filters, name="makam-filters"),
]
