# -*- coding: utf-8 -*-
"""Removed /web-development/ and /web-applications/ — 301 to home."""
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import translation

from apps.core.sitemaps import StaticViewSitemap


class RemovedServicePagesTests(TestCase):
    def test_reverse_names_gone(self):
        for name in ('web_development', 'web_applications'):
            with self.assertRaises(NoReverseMatch):
                reverse(name)

    def test_old_slugs_301_to_home(self):
        cases = (
            ('/web-development/', '/'),
            ('/en/web-development/', '/en/'),
            ('/webove-aplikace/', '/'),
            ('/en/webove-aplikace/', '/en/'),
            ('/web-applications/', '/'),
            ('/en/web-applications/', '/en/'),
        )
        for url, target in cases:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 301, url)
            self.assertEqual(response['Location'], target, url)

    def test_sitemap_excludes_removed_pages(self):
        names = set(StaticViewSitemap().items())
        self.assertNotIn('web_development', names)
        self.assertNotIn('web_applications', names)
        self.assertIn('rozrobka_sajtiv', names)
        self.assertIn('dorobka_sajtu', names)

    def test_ads_slugs_reverse(self):
        with translation.override('cs'):
            self.assertEqual(reverse('rozrobka_sajtiv'), '/tvorba-webu/')
            self.assertEqual(reverse('dorobka_sajtu'), '/uprava-webu/')
        with translation.override('en'):
            self.assertEqual(reverse('rozrobka_sajtiv'), '/en/website-development/')
            self.assertEqual(reverse('dorobka_sajtu'), '/en/website-improvement/')
