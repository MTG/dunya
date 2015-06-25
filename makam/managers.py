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
from django.db.models import Q

import makam

class CollectionReleaseManager(models.Manager):
    def with_permissions(self, ids, permission):
        qs = self.get_queryset()
        if ids and ids != "":
            ids = ids.replace(' ','').split(",")
            qs = qs.filter(collection__mbid__in=ids)
        return qs.filter(collection__permission__in=permission)

class CollectionRecordingManager(models.Manager):
    def with_permissions(self, ids, permission): 
        qs = self.get_queryset()
        if ids and ids != "":
            ids = ids.replace(' ','').split(",")
            qs = qs.filter(release__collection__mbid__in=ids)
        return qs.filter(release__collection__permission__in=permission)

class UnaccentManager(models.Manager):
    """ A manager to use postgres' unaccent module to get items
    with a specified `name` field """
    def unaccent_get(self, name):
        return super(UnaccentManager, self).get_queryset().extra(where=["unaccent(lower(name)) = unaccent(lower(%s))"], params=[name]).get()


class MakamFormManager(UnaccentManager):
    def fuzzy(self, name):
        try:
            return makam.models.Form.objects.get(name__iexact=name)
        except makam.models.Form.DoesNotExist as e:
            try:
                alias = makam.models.FormAlias.objects.get(name__iexact=name)
                return alias.form
            except makam.models.FormAlias.DoesNotExist:
                raise e

class MakamUsulManager(UnaccentManager):
    def fuzzy(self, name):
        try:
            return makam.models.Usul.objects.get(name__iexact=name)
        except makam.models.Usul.DoesNotExist as e:
            try:
                alias = makam.models.UsulAlias.objects.get(name__iexact=name)
                return alias.usul
            except makam.models.UsulAlias.DoesNotExist:
                raise e

class MakamFuzzyManager(UnaccentManager):
    def fuzzy(self, name):
        try:
            return makam.models.Makam.objects.get(name__iexact=name)
        except makam.models.Makam.DoesNotExist as e:
            try:
                alias = makam.models.MakamAlias.objects.get(name__iexact=name)
                return alias.makam
            except makam.models.MakamAlias.DoesNotExist:
                raise e

