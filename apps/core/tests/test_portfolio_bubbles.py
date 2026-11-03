# -*- coding: utf-8 -*-
"""The /portfolio/ category bubbles: canon markup, Czech/EU cases first, CS+EN, no Cyrillic."""
import re

from django.conf import settings
from django.test import TestCase
from django.utils import translation

from apps.core.mixins import portfolio_page_projects
from apps.core.models import PortfolioProject
from apps.core.portfolio_categories import CATEGORY_ORDER, FILTER_ALL

CYRILLIC_RE = re.compile(r'[А-Яа-яІіЇїЄєҐґ]')


class PortfolioOrderTests(TestCase):
    """Canon shows every published case; the Czech site puts non-Ukrainian ones first."""

    def setUp(self):
        for slug, order, ukraine in (
            ('ua-early', 1, True),
            ('eu-late', 90, False),
            ('ua-late', 91, True),
            ('eu-early', 2, False),
        ):
            PortfolioProject.objects.create(
                slug=slug, title=slug, order=order, is_published=True,
                show_on_portfolio=True, is_ukraine_client=ukraine,
            )

    def test_non_ukraine_cases_come_first(self):
        slugs = [p.slug for p in portfolio_page_projects()]
        self.assertEqual(slugs, ['eu-early', 'eu-late', 'ua-early', 'ua-late'])

    def test_snap_index_follows_the_displayed_order(self):
        projects = portfolio_page_projects()
        self.assertEqual([p.snap_index for p in projects], list(range(len(projects))))


class PortfolioBubbleMarkupTests(TestCase):
    def setUp(self):
        for index, category in enumerate(CATEGORY_ORDER):
            PortfolioProject.objects.create(
                slug=f'case-{category}', title=f'Case {category}', order=index,
                category=category, is_published=True, show_on_portfolio=True,
            )

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_one_bubble_per_category_plus_all(self):
        html = self.client.get('/portfolio/').content.decode()
        keys = re.findall(r'data-pf-filter="([^"]+)"', html)
        self.assertEqual(keys, [FILTER_ALL, *CATEGORY_ORDER])

    def test_first_bubble_is_the_pressed_one(self):
        html = self.client.get('/portfolio/').content.decode()
        bubbles = re.findall(r'<button[^>]*data-pf-filter="[^"]*"[^>]*>', html, re.S)
        block = html[html.index('data-pf-bar-list'):]
        first = block[:block.index('</button>')]
        self.assertIn('is-active', first)
        self.assertIn('aria-pressed="true"', first)
        self.assertEqual(sum('aria-pressed="true"' in b for b in bubbles), 1)
        for bubble in bubbles:
            self.assertIn('aria-controls="pf-projects"', bubble)

    def test_canon_refinement_stylesheet_is_linked(self):
        html = self.client.get('/portfolio/').content.decode()
        self.assertIn('css/pages/tz-sofia-20261028.css', html)

    def test_labels_are_localized_and_latin(self):
        for path, expected in (
            ('/portfolio/', ['Všechny projekty', 'E-shopy', 'Firemní weby']),
            ('/en/portfolio/', ['All projects', 'Online stores', 'Corporate websites']),
        ):
            html = self.client.get(path).content.decode()
            for label in expected:
                self.assertIn(label, html, path)
            leaks = sorted(set(CYRILLIC_RE.findall(html)))
            self.assertEqual(leaks, [], f'{path}: {leaks}')


class PortfolioBubbleStyleTests(TestCase):
    """The mobile bubble grid and the hero scrim come from canon's refinement sheet."""

    def setUp(self):
        self.css = (settings.BASE_DIR / 'static' / 'css' / 'pages'
                    / 'tz-sofia-20261028.css').read_text(encoding='utf-8')

    def test_hero_carries_the_canon_scrim(self):
        self.assertIn('.pfg-hero__bg::after', self.css)
        self.assertIn('rgba(0, 0, 0, .45)', self.css)

    def test_all_bubble_spans_the_mobile_row(self):
        self.assertIn('.pfg-filter[data-pf-filter="all"]', self.css)
        self.assertIn('grid-column: 1 / -1', self.css)

    def test_mobile_bubbles_keep_a_44px_touch_target(self):
        self.assertIn('min-height: 44px', self.css)

    def test_no_important_in_declarations(self):
        declarations = re.sub(r'/\*.*?\*/', '', self.css, flags=re.S)
        self.assertNotIn('!important', declarations)
