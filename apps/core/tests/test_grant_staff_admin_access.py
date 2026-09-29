"""Тести для grant_staff_admin_access management command."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.core.admin_permissions import STAFF_ADMIN_USERNAME


class GrantStaffAdminAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username=STAFF_ADMIN_USERNAME,
            email='valeria@prometeylabs.com',
            password='test-pass-123',
        )

    def test_grants_staff_access_without_superuser(self):
        call_command('grant_staff_admin_access', username=STAFF_ADMIN_USERNAME)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.has_perm('core.view_formsubmission'))
        self.assertFalse(self.user.has_perm('auth.view_user'))

    def test_idempotent_on_second_run(self):
        call_command('grant_staff_admin_access', username=STAFF_ADMIN_USERNAME)
        call_command('grant_staff_admin_access', username=STAFF_ADMIN_USERNAME)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.has_perm('core.view_formsubmission'))

    def test_skips_missing_user_without_error(self):
        # Fresh Render deploys must not fail when staff user is not seeded yet.
        call_command('grant_staff_admin_access', username='NonExistentUser')

    def test_can_manage_admin_users_callback(self):
        from apps.core.admin_permissions import can_manage_admin_users
        from django.test import RequestFactory

        User = get_user_model()
        factory = RequestFactory()

        staff_request = factory.get('/admin/')
        staff_request.user = self.user
        self.assertFalse(can_manage_admin_users(staff_request))

        superuser = User.objects.create_superuser(
            username='SofiaDmitrenko',
            email='sofia@prometeylabs.com',
            password='test-pass-456',
        )
        super_request = factory.get('/admin/')
        super_request.user = superuser
        self.assertTrue(can_manage_admin_users(super_request))
