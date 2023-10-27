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
from django.utils import timezone
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


class AccessRequestManager(models.Manager):
    def for_user(self, user):
        requests = self.get_queryset().filter(user=user).order_by('-requestdate')
        if requests.count():
            return requests[0]
        return None

    def unapproved(self):
        return self.get_queryset().filter(approved__isnull=True)


class AccessRequest(models.Model):
    class Meta:
        ordering = ['requestdate']

    objects = AccessRequestManager()

    user = models.ForeignKey(User, unique=False, on_delete=models.CASCADE)
    requestdate = models.DateTimeField(default=timezone.now)
    justification = models.TextField()
    approved = models.BooleanField(null=True)
    processedby = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='access_request_approvals')
    processeddate = models.DateTimeField(blank=True, null=True)

    def approve_or_deny_request(self, user, approved):
        """Approve or deny this request
        Arguments:
            user: the user who processed this request
            approved: the decision (True for approved, False for denied)
        """
        self.approved = approved
        self.processedby = user
        self.processeddate = timezone.now()

    def __str__(self):
        return f'User: {self.user}, Date: {self.requestdate}, approved: {self.approved}'
