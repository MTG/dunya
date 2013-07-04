from django.core.management.base import BaseCommand, CommandError

import inspect

from dashboard import models
from dashboard import jobs

class Command(BaseCommand):
    help = 'Create database data based on static data defined in code'

    def handle(self, *args, **options):
        prefix = 'dashboard.jobs.'
        for name, checker in inspect.getmembers(jobs, inspect.isclass):
            if issubclass(checker, jobs.CompletenessBase) and not name.endswith('CompletenessBase'):
                path = "%s%s" % (prefix, name)
                if models.CompletenessChecker.objects.filter(module=path).count() == 0:
                    if hasattr(checker, "name"):
                        name = checker.name
                    models.CompletenessChecker.objects.create(module=path, type=checker.type, name=name)

