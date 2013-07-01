from django.db.models.signals import post_syncdb

import pkgutil
import inspect

from dashboard import models
from dashboard import jobs

def create_completeness_tasks(sender, **kwargs):
    prefix = 'dashboard.jobs.'
    for name, checker in inspect.getmembers(jobs, inspect.isclass):
        if issubclass(checker, jobs.CompletenessBase) and not name.endswith('CompletenessBase'):
            path = "%s%s" % (prefix, name)
            if models.CompletenessChecker.objects.filter(module=path).count() == 0:
                if hasattr(checker, "name"):
                    name = checker.name
                models.CompletenessChecker.objects.create(module=path, type=checker.type, name=name)

post_syncdb.connect(create_completeness_tasks)
