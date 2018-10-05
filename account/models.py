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

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return str(self.user)


def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created:
        p = UserProfile()
        p.user = instance
        p.save()
        Token.objects.create(user=instance)


post_save.connect(user_post_save, sender=User)

