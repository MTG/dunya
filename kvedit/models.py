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
import json

class Category(models.Model):
    name = models.CharField(max_length=200)
    source_file_type = models.ForeignKey("docserver.SourceFileType", blank=True, null=True)

    def __str__(self):
        return ('%s' % self.name)

    def to_json(self):
        return json.dumps(self.to_object())

    def to_object(self):
        c = []
        for i in self.items.all():
            c.append(i.to_object())
        return c

class Item(models.Model):
    category = models.ForeignKey(Category, related_name="items")
    ref = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)
    reverify = models.BooleanField(default=False)

    def to_json(self):
        return json.dumps(self.to_object())

    def to_object(self):
        ret = {}
        for f in self.fields.all():
            ret[f.key] = f.value
        return ret

class Field(models.Model):
    item = models.ForeignKey(Item, related_name="fields")
    key = models.CharField(max_length=200)
    value = models.TextField()
    modified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        ''' On save, update modified value '''
        if self.id:
            self.modified = True
        return super(Field, self).save(*args, **kwargs)
