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

import carnatic

class BootlegConcertManager(models.Manager):
    use_for_related_fields = True

    def with_bootlegs(self, show_bootlegs):
        qs = self.get_queryset()
        if not show_bootlegs:
            qs = qs.filter(bootleg=False)
        return qs

    def with_user_permission(self, ids, is_staff=False, is_restricted=False):
        qs = self.get_queryset()
        if ids == None:
            return qs.none()
        else:
            ids = ids.replace(' ','').split(",")
        permission = self._get_permissions(is_staff, is_restricted)
        return qs.filter(collection__mbid__in=ids, collection__permission__in=permission)

    def with_user_permission(self, is_staff=False, is_restricted=False):     
        permission = self._get_permissions(is_staff, is_restricted)
        return self.get_queryset().filter(collection__permission__in=permission)

    def _get_permissions(self, is_staff, is_restricted):
        permission = ["U"]
        if is_staff:
            permission = ["S", "R", "U"]
        elif is_restricted:
            permission = ["R", "U"]
        return permission


class BootlegRecordingManager(models.Manager):
    use_for_related_fields = True

    def with_bootlegs(self, show_bootlegs):
        qs = self.get_queryset()
        if not show_bootlegs:
            qs = qs.filter(concert__bootleg=False)
        return qs

class CarnaticRaagaManager(models.Manager):
    def fuzzy(self, name):
        try:
            return carnatic.models.Raaga.objects.get(Q(name__iexact=name) | Q(common_name__iexact=name))
        except carnatic.models.Raaga.DoesNotExist as e:
            try:
                alias = carnatic.models.RaagaAlias.objects.get(name__iexact=name)
                return alias.raaga
            except carnatic.models.RaagaAlias.DoesNotExist:
                raise e

class CarnaticTaalaManager(models.Manager):
    def fuzzy(self, name):
        try:
            return carnatic.models.Taala.objects.get(Q(name__iexact=name) | Q(common_name__iexact=name))
        except carnatic.models.Taala.DoesNotExist as e:
            try:
                alias = carnatic.models.TaalaAlias.objects.get(name__iexact=name)
                return alias.taala
            except carnatic.models.TaalaAlias.DoesNotExist:
                raise e

class CarnaticFormManager(models.Manager):
    def fuzzy(self, name):
        try:
            return carnatic.models.Form.objects.get(name__iexact=name)
        except carnatic.models.Form.DoesNotExist as e:
            try:
                alias = carnatic.models.FormAlias.objects.get(name__iexact=name)
                return alias.form
            except carnatic.models.FormAlias.DoesNotExist:
                raise e

class CarnaticInstrumentManager(models.Manager):
    def fuzzy(self, name):
        try:
            return carnatic.models.Instrument.objects.get(name__iexact=name)
        except carnatic.models.Instrument.DoesNotExist as e:
            try:
                alias = carnatic.models.InstrumentAlias.objects.get(name__iexact=name)
                return alias.instrument
            except carnatic.models.InstrumentAlias.DoesNotExist:
                raise e

class FuzzySearchManager(models.Manager):
    def fuzzy(self, name):
        name = name.lower()
        try:
            return self.model.objects.get(name__iexact=name)
        except self.model.DoesNotExist:
            items = self.model.objects.all()
            names = []
            for i in items:
                names.append(i.name.lower())
                if hasattr(i, "common_name"):
                    names.append(i.common_name.lower())
            dups = stringDuplicates.stringDuplicates(name, names, stripped=True)
            if len(dups) != 1:
                raise self.model.DoesNotExist()
            n = dups[0]
            for i in items:
                if i.name.lower() == n.lower():
                    return i
            raise self.model.DoesNotExist()
