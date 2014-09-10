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

from django.core.management.base import BaseCommand

from carnatic import models
from dashboard import external_data

class Command(BaseCommand):
    help = 'Load descriptions and images for carnatic instruments'
    args = '[overwrite]'

    def handle(self, *args, **options):
        instruments = models.Instrument.objects.all()
        overwrite = False
        if len(args):
            print "overwrite"
            return
            overwrite = True
        for i in instruments:
            print "Loading instrument data for", i
            external_data.import_instrument_description(i, overwrite)
