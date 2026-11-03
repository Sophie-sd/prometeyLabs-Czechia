# -*- coding: utf-8 -*-
"""Project external URLs point at the client's English version where one exists.

The audit behind these expectations is in round2/link_mapping.md: every URL in
PORTFOLIO_PROJECTS and HOME_CLIENTS was fetched and checked for hreflang en, a
language switch and /en/. The eight below have a real English version; the rest
either have none or (carpet-haus) only swap the `lang` attribute.
"""
from urllib.parse import urlparse

from django.test import SimpleTestCase

from apps.core.portfolio_seed_data import HOME_CLIENTS, PORTFOLIO_PROJECTS

ENGLISH_VERSION = {
    'deksor': 'https://led-leader.com.ua/en/',
    'fpsu': 'https://www.fpsu.org.ua/en/',
    'magnum': 'https://magnum-tpc.com/en/',
    'notenhaus': 'https://notenhaus.com.ua/en/',
    'recharge': 'https://recharge4gym.com.ua/en/',
    'svitpc': 'https://svitpc.com.ua/en/',
    'ucvn': 'https://ucvn.com.ua/en/',
    'zatyshnyi-dvir': 'https://zatyshnyidvir.com/en/',
}

# Checked and intentionally not switched.
KEPT = {
    'carpet-haus': 'https://carpet-haus.com.ua/',          # /en/ = the same Ukrainian page
    'distageavto': 'https://www.distageavto.com/uk/',      # /uk/ is the site's only locale
}


def by_slug():
    return {item['slug']: item for item in PORTFOLIO_PROJECTS}


class ProjectEnglishLinkTests(SimpleTestCase):
    def test_projects_with_an_english_version_use_it(self):
        projects = by_slug()
        for slug, expected in ENGLISH_VERSION.items():
            self.assertIn(slug, projects)
            self.assertEqual(projects[slug].get('site_url'), expected, slug)

    def test_audited_exceptions_keep_the_original_url(self):
        projects = by_slug()
        for slug, expected in KEPT.items():
            self.assertEqual(projects[slug].get('site_url'), expected, slug)

    def test_only_audited_projects_keep_a_ukrainian_locale_prefix(self):
        """A /uk/ URL sends a Czech or English reader to the Ukrainian page."""
        for item in PORTFOLIO_PROJECTS:
            path = urlparse(item.get('site_url') or '').path
            if item['slug'] in KEPT:
                continue
            self.assertNotRegex(path, r'^/(uk|ua|ru)(/|$)', item['slug'])

    def test_every_external_url_is_https(self):
        for item in list(PORTFOLIO_PROJECTS) + list(HOME_CLIENTS):
            url = item.get('site_url') or ''
            if url:
                self.assertTrue(url.startswith('https://'), url)
