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

from carnatic import models as carnatic_models
from hindustani import models as hindustani_models
import collections

class Command(BaseCommand):
    help = "Find each artist's main instrument and fill in the field"

    def handle(self, *args, **options):
        if len(args) == 0 or args[0] not in ('carnatic', 'hindustani'):
            raise CommandError("""Missing argument. The argument passed to this
                                command should be one of \'carnatic\' or 
                                \'hindustani\'i""")
        models = {  'carnatic':     carnatic_models,
                    'hindustani':   hindustani_models,
                 }[args[0]]
        artists = models.Artist.objects.all()
        for a in artists:
            counter = collections.Counter()
            for ip in a.instrumentperformance_set.all():
                counter[ip.instrument] += 1
            if models == carnatic_models:
                for ip in a.instrumentconcertperformance_set.all():
                    counter[ip.instrument] += 1
            try:
                common = counter.most_common(1)[0]
                inst = common[0]
                a.main_instrument = inst
                a.save()
            except IndexError:
                pass


