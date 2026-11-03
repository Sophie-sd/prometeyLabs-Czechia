"""Tests for demoshop app: slug generation and migrations."""
import importlib

from django.contrib.auth.models import Group, Permission
from django.test import TestCase, TransactionTestCase

from apps.demoshop.models import DemoShop


class SlugGenerationTestCase(TestCase):
    """Test ASCII slug generation with diacritics stripping."""

    def test_generate_slug_strips_diacritics(self):
        """Slug should be ASCII-only, even with Czech diacritics."""
        test_cases = [
            ('Jaroslav Bukáček', 'jaroslav-bukacek'),
            ('Průmyslová výroba', 'prumyslova-vyroba'),
            ('Žluťoučký kůň', 'zlutoucky-kun'),
            ('Café Résumé', 'cafe-resume'),
        ]
        
        for input_name, expected_stem in test_cases:
            with self.subTest(input_name=input_name):
                slug = DemoShop.generate_slug(input_name)
                # Should start with expected ASCII stem
                self.assertTrue(slug.startswith(expected_stem))
                # Should end with hex token (6 chars after dash)
                self.assertEqual(len(slug), len(expected_stem) + 1 + 6)
                # Should be all ASCII
                self.assertTrue(slug.isascii())

    def test_generate_slug_fallback_to_shop(self):
        """Empty or whitespace-only input should fallback to 'shop'."""
        for empty_input in ['', '   ', '!!!']:
            with self.subTest(input=empty_input):
                slug = DemoShop.generate_slug(empty_input)
                self.assertTrue(slug.startswith('shop-'))

    def test_demo_login_is_ascii(self):
        """Demo login derived from slug should also be ASCII."""
        slug = DemoShop.generate_slug('Jaroslav Bukáček')
        demo_login = f'shop-{slug}'[:150]
        self.assertTrue(demo_login.isascii())
        self.assertIn('jaroslav-bukacek', demo_login)


class DemoClientPermsMigrationTestCase(TransactionTestCase):
    """Test 0007 migration: DemoClient permissions backfill."""

    def test_democlient_group_has_permissions(self):
        """DemoClient group should have all permissions from DEMO_CLIENT_PERMS."""
        # Import the permissions list using importlib (can't import module starting with digit)
        m0002 = importlib.import_module('apps.demoshop.migrations.0002_democlient_group')
        DEMO_CLIENT_PERMS = m0002.DEMO_CLIENT_PERMS
        
        # Get the group (should be created by migration)
        try:
            group = Group.objects.get(name='DemoClient')
        except Group.DoesNotExist:
            self.fail('DemoClient group should exist after migrations')
        
        # Check that group has the expected permissions
        group_perms = group.permissions.all()
        group_codenames = {
            (p.content_type.app_label, p.codename) 
            for p in group_perms
        }
        
        # All permissions from DEMO_CLIENT_PERMS should be assigned
        for app_label, codename in DEMO_CLIENT_PERMS:
            with self.subTest(perm=f'{app_label}.{codename}'):
                # Check if permission exists in auth system
                if Permission.objects.filter(
                    content_type__app_label=app_label,
                    codename=codename
                ).exists():
                    self.assertIn(
                        (app_label, codename),
                        group_codenames,
                        f'Permission {app_label}.{codename} should be in DemoClient group'
                    )
