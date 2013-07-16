from django.core.management.base import BaseCommand, CommandError

import inspect
import re

from dashboard import models
from dashboard import jobs

class Command(BaseCommand):
    help = 'Create database data based on static data defined in code'

    def handle(self, *args, **options):
        prefix = 'dashboard.jobs.'
        all_classes = []
        for name, checker in inspect.getmembers(jobs, inspect.isclass):
            if issubclass(checker, jobs.CompletenessBase) and not name.endswith('CompletenessBase'):
                path = "%s%s" % (prefix, name)
                all_classes.append(path)
                if models.CompletenessChecker.objects.filter(module=path).count() == 0:
                    if hasattr(checker, "name"):
                        name = checker.name
                    else:
                        # If no name, split on camel case
                        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
                    models.CompletenessChecker.objects.create(module=path, type=checker.type, name=name)
        # Remove any items in the DB that no longer have a class
        for i in models.CompletenessChecker.objects.all():
            if i.module not in all_classes:
                print "deleting", i
                models.CompletenessChecker.objects.filter(module=i.module).delete()

