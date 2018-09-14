from django.db import models
from django.db.models import Q

import jingju.models


class CollectionReleaseManager(models.Manager):
    use_for_related_fields = True

    def with_permissions(self, ids, permission):
        qs = self.get_queryset()
        if ids and ids != '':
            ids = ids.replace(' ', '').split(',')
            qs = qs.filter(collection__collectionid__in=ids)
        return qs.filter(collection__permission__in=permission)


class CollectionRecordingManager(models.Manager):
    use_for_related_fields = True

    def with_permissions(self, ids, permission):
        qs = self.get_queryset()
        if ids and ids != '':
            ids = ids.replace(' ', '').split(',')
            qs = qs.filter(release__collection__collectionid__in=ids)
        if permission:
            qs = qs.filter(release__collection__permission__in=permission)
        return qs



class ArtistManager(models.Manager):
    use_for_related_fields = True

    def with_permissions(self, ids, permission):
        qs = self.get_queryset()
        if ids and ids != '':
            ids = ids.replace(' ', '').split(',')
            # qs = qs.filter(recording__release__collection__permission__in=permission)
            qs = qs.filter(recording__release__collection__collectionid__in=ids).distinct()
            qs = qs.filter(recording__release__collection__permission__in=permission).distinct()
        return qs
