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

from django.db import models

from compmusic.fuzzy import stringDuplicates

class FuzzySearchManager(models.Manager):
    def fuzzy(self, name):
        name = name.lower()
        try:
            return self.model.objects.get(name__iexact=name)
        except self.model.DoesNotExist:
            items = self.model.objects.all()
            names = [i.name.lower() for i in items]
            dups = stringDuplicates.stringDuplicates(name, names, stripped=True)
            if len(dups) != 1:
                raise self.model.DoesNotExist()
            n = dups[0]
            for i in items:
                if i.name.lower() == n.lower():
                    return i
            raise Exception("Whoops")

