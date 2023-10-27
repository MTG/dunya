from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from account.models import AccessRequest


class UserAdminTest(TestCase):
    """Test the admin of new users (new user approval and group permissions)"""

    def setUp(self):
        self.adminuser = User.objects.create_superuser('admin', email='admin@example.com', password='password')
        self.newuser1 = User.objects.create_user('userone', email='userone@example.com', is_active=False)
        self.newuser2 = User.objects.create_user('usertwo', email='usertwo@example.com', is_active=False)

    def test_get_new_users_for_approval(self):
        self.client.force_login(self.adminuser)
        res = self.client.get(reverse('dashboard-accounts'))
        self.assertEqual(2, len(res.context['user_formset']))

    @mock.patch('dashboard.email.email_user_on_account_approval')
    def test_approve_new_account(self, email_mock):
        self.client.force_login(self.adminuser)

        self.assertEqual(2, User.objects.filter(is_active=False).count())

        data = {'form-TOTAL_FORMS': ['1'],  'submit': ['Approve accounts'],
                'form-MAX_NUM_FORMS': ['1000'], 'form-1-is_active': ['on'],
                'form-0-is_active': ['on'], 'form-INITIAL_FORMS': ['2'],
                'form-MIN_NUM_FORMS': ['0'], 'form-0-id': [str(self.newuser1.id)]}
        self.client.post(reverse('dashboard-accounts'), data=data)

        email_mock.assert_called_with(mock.ANY, self.newuser1)
        self.assertEqual(1, User.objects.filter(is_active=False).count())
        self.assertEqual(self.newuser2, User.objects.filter(is_active=False)[0])

        self.newuser1.refresh_from_db()
        self.assertTrue(self.newuser1.is_active)

    def test_delete_new_account(self):
        self.client.force_login(self.adminuser)

        self.assertEqual(2, User.objects.filter(is_active=False).count())

        data = {'form-TOTAL_FORMS': ['1'],  'submit': ['Approve accounts'],
                'form-MAX_NUM_FORMS': ['1000'], 'form-1-is_active': ['on'],
                'form-0-delete': ['on'], 'form-INITIAL_FORMS': ['2'],
                'form-MIN_NUM_FORMS': ['0'], 'form-0-id': [str(self.newuser1.id)]}
        self.client.post(reverse('dashboard-accounts'), data=data)

        self.assertEqual(1, User.objects.filter(is_superuser=False).count())
        try:
            self.newuser1.refresh_from_db()
            self.fail('newuser1 should have been deleted')
        except User.DoesNotExist:
            pass

    def test_get_users_for_accessrequest(self):
        self.newuser1.is_active = True
        self.newuser1.save()

        AccessRequest.objects.create(user=self.newuser1, justification='I want to use this site')

        self.client.force_login(self.adminuser)
        res = self.client.get(reverse('dashboard-accounts'))
        self.assertEqual(1, len(res.context['access_formset']))

    @mock.patch('account.services.add_user_to_restricted_group')
    @mock.patch('dashboard.email.email_user_on_access_request_approval')
    def test_approve_restricted_access(self, email_mock, add_to_group_mock):
        self.newuser1.is_active = True
        self.newuser1.save()
        self.newuser2.is_active = True
        self.newuser2.save()

        areq1 = AccessRequest.objects.create(user=self.newuser1, justification='I want to use this site')
        areq2 = AccessRequest.objects.create(user=self.newuser2, justification='I want to use this site')

        data = {'form-TOTAL_FORMS': ['2'], 'form-MAX_NUM_FORMS': ['1000'], 'form-1-id': [str(areq2.id)],
                'form-0-id': [str(areq1.id)], 'form-MIN_NUM_FORMS': ['0'], 'form-0-decision': ['approve'],
                'submit': ['Approve requests'], 'form-INITIAL_FORMS': ['2']}
        self.client.force_login(self.adminuser)
        self.client.post(reverse('dashboard-accounts'), data=data)

        areq1.refresh_from_db()
        areq2.refresh_from_db()

        self.assertTrue(areq1.approved)
        self.assertEqual(self.adminuser, areq1.processedby)
        self.assertIsNotNone(areq1.processeddate)
        self.assertIsNone(areq2.approved)

        email_mock.assert_called_with(mock.ANY, self.newuser1, True)
        add_to_group_mock.assert_called_with(self.newuser1)

        self.assertEqual(1, AccessRequest.objects.unapproved().count())

    @mock.patch('account.services.add_user_to_restricted_group')
    @mock.patch('dashboard.email.email_user_on_access_request_approval')
    def test_deny_restricted_access(self, email_mock, add_to_group_mock):
        self.newuser1.is_active = True
        self.newuser1.save()
        self.newuser2.is_active = True
        self.newuser2.save()

        areq1 = AccessRequest.objects.create(user=self.newuser1, justification='I want to use this site')
        areq2 = AccessRequest.objects.create(user=self.newuser2, justification='I want to use this site')

        data = {'form-TOTAL_FORMS': ['2'], 'form-MAX_NUM_FORMS': ['1000'], 'form-1-id': [str(areq2.id)],
                'form-0-id': [str(areq1.id)], 'form-MIN_NUM_FORMS': ['0'], 'form-0-decision': ['deny'],
                'submit': ['Approve requests'], 'form-INITIAL_FORMS': ['2']}
        self.client.force_login(self.adminuser)
        self.client.post(reverse('dashboard-accounts'), data=data)

        areq1.refresh_from_db()
        areq2.refresh_from_db()

        self.assertFalse(areq1.approved)
        self.assertEqual(self.adminuser, areq1.processedby)
        self.assertIsNotNone(areq1.processeddate)
        self.assertIsNone(areq2.approved)

        email_mock.assert_called_with(mock.ANY, self.newuser1, False)
        add_to_group_mock.assert_called_with(self.newuser1)

        self.assertEqual(1, AccessRequest.objects.unapproved().count())
