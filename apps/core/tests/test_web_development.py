# -*- coding: utf-8 -*-
"""/web-development/ and /webove-aplikace/ (en: /en/web-applications/) — restored Ads landings."""
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import translation

from apps.core.sitemaps import StaticViewSitemap


class RestoredServicePagesTests(TestCase):
    """Ads landings restored (were 301 → home since bbf7ca4)."""

    def test_reverse_names(self):
        with translation.override('cs'):
            self.assertEqual(reverse('web_development'), '/web-development/')
            self.assertEqual(reverse('web_applications'), '/webove-aplikace/')
        with translation.override('en'):
            self.assertEqual(reverse('web_development'), '/en/web-development/')
            self.assertEqual(reverse('web_applications'), '/en/web-applications/')

    def test_other_language_slug_301_to_canonical(self):
        for url, target in (('/web-applications/', '/webove-aplikace/'),
                            ('/en/webove-aplikace/', '/en/web-applications/')):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 301, url)
            self.assertEqual(response['Location'], target, url)

    def test_sitemap_includes_pages(self):
        names = set(StaticViewSitemap().items())
        for n in ('web_development', 'web_applications', 'rozrobka_sajtiv', 'dorobka_sajtu'):
            self.assertIn(n, names)

    def test_ads_slugs_reverse(self):
        with translation.override('cs'):
            self.assertEqual(reverse('rozrobka_sajtiv'), '/tvorba-webu/')
            self.assertEqual(reverse('dorobka_sajtu'), '/uprava-webu/')
        with translation.override('en'):
            self.assertEqual(reverse('rozrobka_sajtiv'), '/en/website-development/')
            self.assertEqual(reverse('dorobka_sajtu'), '/en/website-improvement/')
