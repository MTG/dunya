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

