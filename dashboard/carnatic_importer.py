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

import django.utils.timezone

from dashboard.log import logger
from dashboard import release_importer

import carnatic
import data

class CarnaticReleaseImporter(release_importer.ReleaseImporter):
    _ArtistClass = carnatic.models.Artist
    _ComposerClass = carnatic.models.Composer
    _ReleaseClass = carnatic.models.Concert
    _RecordingClass = carnatic.models.Recording
    _InstrumentClass = carnatic.models.Instrument

    def get_raaga(self, raaganame):
        try:
            return carnatic.models.Raaga.objects.fuzzy(name=raaganame)
        except carnatic.models.Raaga.DoesNotExist, e:
            try:
                alias = carnatic.models.RaagaAlias.objects.fuzzy(name=raaganame)
                return alias.raaga
            except carnatic.models.RaagaAlias.DoesNotExist, e:
                return None

    def get_taala(self, taalaname):
        try:
            return carnatic.models.Taala.objects.fuzzy(name=taalaname)
        except carnatic.models.Taala.DoesNotExist, e:
            try:
                alias = carnatic.models.TaalaAlias.objects.fuzzy(name=taalaname)
                return alias.taala
            except carnatic.models.TaalaAlias.DoesNotExist, e:
                return None

    def _get_raaga(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_raaga(name):
                ret.append( (seq, compmusic.tags.parse_raaga(name)) )
                seq += 1
        return ret

    def _get_taala(self, taglist):
        ret = []
        seq = 1
        for t in taglist:
            name = t["name"].lower()
            if compmusic.tags.has_taala(name):
                ret.append( (seq, compmusic.tags.parse_taala(name)) )
                seq += 1
        return ret
