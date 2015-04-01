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

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return ('%s' % self.name)

class Item(models.Model):
    category = models.ForeignKey(Category, related_name="items") 
    ref = models.CharField(max_length=200)

class Field(models.Model):
    item = models.ForeignKey(Item, related_name="fields")  
    key = models.CharField(max_length=200)
    value = models.TextField()
    modified = models.BooleanField(default=False)

