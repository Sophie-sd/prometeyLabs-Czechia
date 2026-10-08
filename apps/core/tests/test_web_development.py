# -*- coding: utf-8 -*-
import re

from django.core.cache import cache
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.sitemaps import StaticViewSitemap
from apps.core.utils import SITE_CONTACT_CACHE_KEY


CYRILLIC_RE = re.compile(r'[А-Яа-яІіЇїЄєҐґ]')


class WebDevelopmentPageTests(TestCase):
    def setUp(self):
        # Migration 0010 creates an empty-ish SiteContact row; seed fills
        # legal_name_cs / legal_name_en so the shared footer has no Cyrillic.
        call_command('seed_site_contact_settings')
        cache.delete(SITE_CONTACT_CACHE_KEY)
        self.client = Client()

    def test_reverse_slug(self):
        with translation.override('cs'):
            self.assertEqual(reverse('web_development'), '/web-development/')
        with translation.override('en'):
            self.assertEqual(reverse('web_development'), '/en/web-development/')

    def test_cs_page_ok(self):
        response = self.client.get('/web-development/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')
        self.assertIn('<html lang="cs">', html)
        self.assertIn('hreflang="cs"', html)
        self.assertIn('hreflang="en"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertIn('css/web-development.css', html)
        self.assertIn('js/web-development.js', html)
        self.assertIn('action="/forms/submit/"', html)
        self.assertIsNone(CYRILLIC_RE.search(html), msg='Cyrillic leaked into CS HTML')

    def test_en_page_ok(self):
        response = self.client.get('/en/web-development/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')
        self.assertIn('<html lang="en">', html)
        self.assertIn('hreflang="cs"', html)
        self.assertIn('hreflang="en"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertIn('action="/en/forms/submit/"', html)
        self.assertIn('Turnkey websites for projects of any complexity', html)
        self.assertIn('Request a consultation', html)
        self.assertIsNone(CYRILLIC_RE.search(html), msg='Cyrillic leaked into EN HTML')

    def test_sitemap_includes_page(self):
        names = set(StaticViewSitemap().items())
        self.assertIn('web_development', names)
