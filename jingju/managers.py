from typing import List

from django.db import models


class CollectionReleaseManager(models.Manager):
    use_for_related_fields = True

    def with_permissions(self, ids: List[str], permission):
        qs = self.get_queryset()
        if ids:
            qs = qs.filter(collection__collectionid__in=ids)
        return qs.filter(collection__permission__in=permission)


class CollectionRecordingManager(models.Manager):
    use_for_related_fields = True

    def with_permissions(self, ids: List[str], permission):
        qs = self.get_queryset()
        if ids:
            qs = qs.filter(release__collection__collectionid__in=ids)
        if permission:
            qs = qs.filter(release__collection__permission__in=permission)
        return qs


class ArtistManager(models.Manager):
    use_for_related_fields = True

    def with_permissions(self, ids: List[str], permission):
        qs = self.get_queryset()
        if ids:
            qs = qs.filter(recording__release__collection__collectionid__in=ids).distinct()
            qs = qs.filter(recording__release__collection__permission__in=permission).distinct()
        return qs
