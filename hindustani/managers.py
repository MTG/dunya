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
from typing import List

from django.db import models
from django.db.models import Q

import hindustani.models


class HindustaniRaagManager(models.Manager):
    def fuzzy(self, name):
        try:
            return self.get_queryset().get(Q(name__iexact=name) | Q(common_name__iexact=name))
        except hindustani.models.Raag.DoesNotExist as e:
            try:
                al = hindustani.models.RaagAlias.objects.get(name__iexact=name)
                return al.raag
            except hindustani.models.RaagAlias.DoesNotExist:
                raise e


class HindustaniTaalManager(models.Manager):
    def fuzzy(self, name):
        try:
            return self.get_queryset().get(Q(name__iexact=name) | Q(common_name__iexact=name))
        except hindustani.models.Taal.DoesNotExist as e:
            try:
                al = hindustani.models.TaalAlias.objects.get(name__iexact=name)
                return al.taal
            except hindustani.models.TaalAlias.DoesNotExist:
                raise e


class HindustaniFormManager(models.Manager):
    def fuzzy(self, name):
        try:
            return self.get_queryset().get(Q(name__iexact=name) | Q(common_name__iexact=name))
        except hindustani.models.Form.DoesNotExist as e:
            try:
                al = hindustani.models.FormAlias.objects.get(name__iexact=name)
                return al.form
            except hindustani.models.FormAlias.DoesNotExist:
                raise e


class HindustaniLayaManager(models.Manager):
    def fuzzy(self, name):
        try:
            return self.get_queryset().get(Q(name__iexact=name) | Q(common_name__iexact=name))
        except hindustani.models.Laya.DoesNotExist as e:
            try:
                al = hindustani.models.LayaAlias.objects.get(name__iexact=name)
                return al.laya
            except hindustani.models.LayaAlias.DoesNotExist:
                raise e


class HindustaniInstrumentManager(models.Manager):
    def fuzzy(self, name):
        return self.get_queryset().get(name__iexact=name)


class HindustaniReleaseManager(models.Manager):
    def with_permissions(self, ids: list[str], permission):
        qs = self.get_queryset()
        if ids:
            qs = qs.filter(collection__collectionid__in=ids)
        return qs.filter(collection__permission__in=permission)


class HindustaniRecordingManager(models.Manager):
    def with_permissions(self, ids: list[str], permission):
        qs = self.get_queryset()
        if ids:
            qs = qs.filter(release__collection__collectionid__in=ids)
        return qs.filter(release__collection__permission__in=permission)
