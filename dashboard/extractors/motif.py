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

import essentia.standard

import compmusic.extractors


class MotifExtract(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "motif"

    def run(self, musicbrainzid, fname):
        audio = essentia.standard.MonoLoader(filename=fname)()
        # sankalp to finish

        return [{"starttime": 0, "endtime": 0, "label": ""}]
