# -*- coding: utf-8 -*-
"""Czech fit to Renova: ads LPs, calc_cta, llms.txt, noindex, menu, no UA on public pages."""
import re

from django.test import TestCase
from django.urls import reverse

from apps.core.middleware import is_private_index_path

CYRILLIC_RE = re.compile(r'[А-Яа-яІіЇїЄєҐґ]')


class AdsLandingPagesTests(TestCase):
    def test_cs_and_en_ok(self):
        pages = (
            '/tvorba-webu/',
            '/en/website-development/',
            '/uprava-webu/',
            '/en/website-improvement/',
        )
        for url in pages:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            html = response.content.decode('utf-8')
            self.assertIn('hreflang="cs"', html)
            self.assertIn('hreflang="en"', html)
            self.assertIn('hreflang="x-default"', html)
            self.assertNotIn('hreflang="uk"', html)
            self.assertNotIn('hreflang="ru"', html)
            leaks = sorted(set(CYRILLIC_RE.findall(html)))
            if leaks:
                snippets = re.findall(r'[^<>]{0,20}[А-Яа-яІіЇїЄєҐґ][^<>]{0,40}', html)
                unique = []
                for s in snippets:
                    s = ' '.join(s.split())
                    if s and s not in unique:
                        unique.append(s)
                self.fail(f'Cyrillic leaked into {url}: {unique[:20]!r}')

    def test_wrong_lang_slug_301(self):
        self.assertEqual(self.client.get('/website-development/').status_code, 301)
        self.assertEqual(self.client.get('/en/tvorba-webu/').status_code, 301)
        self.assertEqual(self.client.get('/website-improvement/').status_code, 301)
        self.assertEqual(self.client.get('/en/uprava-webu/').status_code, 301)

    def test_calc_cta_on_home_and_shop(self):
        for url in ('/', '/internet-shop/', '/corporate-website/', '/tvorba-webu/'):
            html = self.client.get(url).content.decode('utf-8')
            self.assertIn('calc-cta', html, url)


class MenuAndFooterFitTests(TestCase):
    def test_home_menu_has_dorobka_not_web_apps(self):
        html = self.client.get('/').content.decode('utf-8')
        self.assertIn('/uprava-webu/', html)
        self.assertNotIn('/webove-aplikace/', html)
        self.assertNotIn('/web-applications/', html)
        header = html.split('</header>', 1)[0]
        self.assertIn('/corporate-website/', header)
        self.assertIn('/internet-shop/', header)
        self.assertIn('/telegram-bot/', header)
        self.assertIn('/calculator/', header)
        self.assertNotIn('nav-dropdown', header)

    def test_footer_services_point_to_pages(self):
        html = self.client.get('/').content.decode('utf-8')
        footer = html[html.index('<footer'):]
        services = footer[:footer.index('plf__col--company')]
        self.assertIn('/tvorba-webu/', services)
        self.assertIn('/uprava-webu/', services)
        self.assertIn('/telegram-bot/', services)
        self.assertIn('/calculator/', services)
        self.assertNotIn('#services', services)


class LlmsAndNoIndexTests(TestCase):
    def test_llms_txt(self):
        response = self.client.get('/llms.txt')
        self.assertEqual(response.status_code, 200)
        text = response.content.decode('utf-8')
        self.assertIn('prometeylabs.cz', text)
        self.assertIn('/tvorba-webu/', text)
        self.assertIn('/uprava-webu/', text)
        self.assertNotIn('https://prometeylabs.com', text)

    def test_private_paths(self):
        self.assertTrue(is_private_index_path('/proposal/acme/'))
        self.assertTrue(is_private_index_path('/en/demo/shop-x/'))
        self.assertFalse(is_private_index_path('/internet-shop/'))

    def test_demo_sets_x_robots(self):
        response = self.client.get('/demo/not-a-shop/')
        self.assertEqual(response.get('X-Robots-Tag'), 'noindex, nofollow')
