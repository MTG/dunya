from django.contrib.auth.models import User
from django.test import TestCase

from account.models import AccessRequest


class AccessRequestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test_user')

    def test_get_access_request_for_user_no_request(self):
        """If a user has no access requests"""

        req = AccessRequest.objects.for_user(self.user)
        self.assertIsNone(req)

    def test_get_access_request_for_user(self):
        req = AccessRequest.objects.create(user=self.user)

        got = AccessRequest.objects.for_user(self.user)
        self.assertEquals(req, got)

    def test_get_access_request_for_user_many(self):
        """If a user has many access requests, return the most recent"""
        req1 = AccessRequest.objects.create(user=self.user, requestdate='2018-11-20 18:00:00+00')
        req2 = AccessRequest.objects.create(user=self.user, requestdate='2018-10-11 12:00:00+00')

        got = AccessRequest.objects.for_user(self.user)
        # most recent
        self.assertEquals(req1, got)
