"""#40: орієнтовна ціна в Kč — до 500 Kč, половина вгору; спільний хелпер."""
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.utils import translation

from apps.core.calculator_estimate import eur_to_czk_rounded, format_price_display
from apps.core.web_development import WEB_DEV_TIERS, web_dev_prices

NB = '\u00a0'
EXPECTED_CZK = {
    'landing': (10000, 17000),
    'corporate': (17000, 24500),
    'shop': (39000, 68500),
    'app': (68500, 196000),
}


class EurToCzkRoundedTests(SimpleTestCase):
    def test_tiers_exact(self):
        for key, low, high in WEB_DEV_TIERS:
            self.assertEqual((eur_to_czk_rounded(low), eur_to_czk_rounded(high)), EXPECTED_CZK[key], key)

    def test_half_up_boundary(self):
        with mock.patch('apps.core.calculator_estimate.EUR_CZK', 25):
            self.assertEqual(eur_to_czk_rounded(10), 500)    # 250 → 500 (round() → 0)
            self.assertEqual(eur_to_czk_rounded(50), 1500)   # 1250 → 1500 (round() → 1000)
            self.assertEqual(eur_to_czk_rounded(Decimal('9.99')), 0)  # 249.75 → 0

    def test_below_and_above_half(self):
        self.assertEqual(eur_to_czk_rounded(Decimal('10.204')), 0)    # 249.998
        self.assertEqual(eur_to_czk_rounded(Decimal('10.205')), 500)  # 250.0225
        self.assertEqual(eur_to_czk_rounded(30.6), 500)               # 749.7
        self.assertEqual(eur_to_czk_rounded(0), 0)

    def test_float_and_decimal_inputs(self):
        self.assertEqual(eur_to_czk_rounded(400.0), 10000)
        self.assertEqual(eur_to_czk_rounded(Decimal('400')), 10000)
        self.assertIsInstance(eur_to_czk_rounded(400), int)

    def test_calculator_secondary(self):
        self.assertEqual(format_price_display(400, 'cs')['price_secondary'], f'orientačně ~10{NB}000 Kč')
        self.assertEqual(format_price_display(1650, 'cs')['price_secondary'], f'orientačně ~40{NB}500 Kč')  # 40 425
        self.assertEqual(format_price_display(550, 'en')['price_secondary'], f'approx. ~13{NB}500 Kč')     # 13 475
        self.assertEqual(format_price_display(400, 'uk')['price_secondary'], '')

    def test_web_dev_prices_strings(self):
        cs = web_dev_prices('cs')
        self.assertEqual(cs['landing']['czk'], f'≈{NB}10{NB}000–17{NB}000{NB}Kč')
        self.assertEqual(cs['app']['czk_from'], f'≈{NB}68{NB}500{NB}Kč')
        en = web_dev_prices('en')
        self.assertEqual(en['shop']['czk'], f'≈{NB}CZK{NB}39,000–68,500')


class WebDevelopmentCzkRenderTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def _czk_spans(self, url):
        import re
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return re.findall(r'data-pl-web-cur="czk"[^>]*>([^<]*)<', response.content.decode())

    def test_cs_page_czk_values(self):
        spans = self._czk_spans('/web-development/')
        self.assertTrue(spans)
        for key, (lo, hi) in EXPECTED_CZK.items():
            rng = f'≈{NB}{lo:,}–{hi:,}{NB}Kč'.replace(',', NB)
            self.assertIn(rng, spans, key)
        for amount in ('10{NB}000', '17{NB}000', '39{NB}000'):  # admin.html «od …»
            self.assertIn(f'≈{NB}' + amount.format(NB=NB) + f'{NB}Kč', spans)
        self.assertFalse(any('9' + NB + '800' in s for s in spans))

    def test_en_page_czk_values(self):
        spans = self._czk_spans('/en/web-development/')
        self.assertTrue(spans)
        for key, (lo, hi) in EXPECTED_CZK.items():
            self.assertIn(f'≈{NB}CZK{NB}{lo:,}–{hi:,}', spans, key)
