# -*- coding: utf-8 -*-
"""The slot-10 flame runs behind the shop CTA strip and the FAQ — both must stay readable."""
import re

from django.conf import settings
from django.test import TestCase
from django.utils import translation

CSS = settings.BASE_DIR / 'static' / 'css'


def rule(path, selector):
    """The declaration block of the first rule whose selector starts with `selector`."""
    css = re.sub(r'/\*.*?\*/', '', path.read_text(encoding='utf-8'), flags=re.S)
    match = re.search(re.escape(selector) + r'[^{}]*\{([^{}]*)\}', css, re.S)
    return ' '.join(match.group(1).split()) if match else None


class ShopFaqSkinTests(TestCase):
    """Canon's shop FAQ sits on solid --pl-panel plates, not on the bare flame."""

    def setUp(self):
        self.css = CSS / 'internet-shop-v2.css'

    def test_faq_item_has_a_solid_panel(self):
        item = rule(self.css, '.pl-shop-body .pl-ads-faq__item')
        self.assertIsNotNone(item)
        self.assertIn('background: var(--pl-panel)', item)
        self.assertIn('border: 0', item)

    def test_faq_summary_replaces_the_default_marker(self):
        summary = rule(self.css, '.pl-shop-body .pl-ads-faq__q')
        self.assertIsNotNone(summary)
        self.assertIn('list-style: none', summary)
        css = self.css.read_text(encoding='utf-8')
        self.assertIn('.pl-ads-faq__q::-webkit-details-marker', css)
        self.assertIn('.pl-shop-body .pl-ads-faq__item[open] > .pl-ads-faq__q::after', css)

    def test_faq_answer_keeps_canon_contrast(self):
        answer = rule(self.css, '.pl-shop-body .pl-ads-faq__a')
        self.assertIsNotNone(answer)
        self.assertIn('color: #c8c8c8', answer)


class ShopCtaStripContrastTests(TestCase):
    def test_strip_copy_carries_the_canon_scrim(self):
        copy = rule(CSS / 'internet-shop-v2-cz.css',
                    '.pl-shop-body .pl-shop__slot10 .pl-corp__calc-promo-title')
        self.assertIsNotNone(copy)
        self.assertIn('text-shadow', copy)

    def test_accent_button_passes_aa_against_white(self):
        """White on #f60 is 2.9:1; canon's #c44e00 is 4.7:1."""
        button = rule(CSS / 'corporate-website-v2.css', '.pl-corp__btn--accent')
        self.assertIsNotNone(button)
        self.assertIn('background: #c44e00', button)
        self.assertNotIn('var(--pl-acc)', button)


class ShopFaqRendersTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_faq_markup_and_body_class_line_up(self):
        for path in ('/internet-shop/', '/en/internet-shop/'):
            html = self.client.get(path).content.decode()
            self.assertIn('pl-shop-body', html, path)
            self.assertIn('class="pl-ads-faq__item"', html, path)
            self.assertIn('class="pl-ads-faq__q"', html, path)
