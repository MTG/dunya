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

from django.core.management.base import BaseCommand, CommandError

from makam import models
from docserver.models import Document

class Command(BaseCommand):
    help = "Update the is_processed field of works"

    def handle(self, *args, **options):
        mbids = Document.objects.filter(derivedfiles__module_version_id=54).values('external_identifier').distinct()
        models.Work.objects.filter(recording__mbid__in=mbids).update(is_processed=True)
