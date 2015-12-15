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

import logging
import dashboard

class ImportLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = {}
        if hasattr(self, "releaseid"):
            extra["releaseid"] = self.releaseid
        kwargs["extra"] = extra
        return (msg, kwargs)

class ImportLogHandler(logging.Handler):
    def handle(self, record):
        releaseid = getattr(record, "releaseid", None)

        if releaseid:
            release = dashboard.models.MusicbrainzRelease.objects.get(pk=releaseid)
            message = "%s: %s" % (record.levelname, record.getMessage())
            release.add_log_message(message)


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

import_base_logger = logging.getLogger('dunya.importer')
import_base_logger.addHandler(ImportLogHandler())
import_base_logger.addHandler(ch)
import_logger = ImportLogAdapter(import_base_logger, {})


logger = logging.getLogger('dunya')
logger.addHandler(ch)
