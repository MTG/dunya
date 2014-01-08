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

import inspect
import re

from docserver import models
from docserver import filetypes

class Command(BaseCommand):
    help = 'Create database data based on static data defined in code'

    def handle(self, *args, **options):
        prefix = 'docserver.filetypes.'
        all_classes = []
        for name, ftype in inspect.getmembers(filetypes, inspect.isclass):
            if issubclass(ftype, filetypes.FileType) and not name == "FileType":
                path = "%s%s" % (prefix, name)
                all_classes.append(ftype.extension)
                if models.SourceFileType.objects.filter(extension=ftype.extension).count() == 0:
                    if hasattr(ftype, "name"):
                        name = ftype.name
                    else:
                        # If no name, split on camel case
                        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
                    models.SourceFileType.objects.create(name=name, extension=ftype.extension)
        # Remove any items in the DB that no longer have a class
        for i in models.SourceFileType.objects.all():
            if i.extension not in all_classes:
                print "deleting", i
                models.FileType.objects.filter(extension=i.extension).delete()

