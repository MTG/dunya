# Copyright 2018 Honglin Ma
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
