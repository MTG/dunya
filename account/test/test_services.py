from django.contrib.auth.models import User
from django.test import TestCase

from account import services


class ServicesTest(TestCase):

    # This fixture uses django "natural keys" to dynamically generate a PK value
    # https://docs.djangoproject.com/en/dev/topics/serialization/#topics-serialization-natural-keys
    fixtures = ['docserver_groups']

    def test_add_user_to_restricted_group(self):
        user = User.objects.create_user('my_testuser')
        self.assertFalse(user.has_perm('docserver.read_restricted'))

        services.add_user_to_restricted_group(user)
        # For the ModelBackend to correctly read permissions we have to reload it
        user = User.objects.get(username='my_testuser')

        self.assertTrue(user.has_perm('docserver.read_restricted'))
