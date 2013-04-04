from django.db import models

from util.fuzzy import stringDuplicates

class FuzzySearchManager(models.Manager):
    def fuzzy(self, name):
        name = name.lower()
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

