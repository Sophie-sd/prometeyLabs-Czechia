"""#40: орієнтовна ціна в Kč — до 500 Kč, половина вгору; спільний хелпер."""
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.utils import translation

from apps.core.calculator_estimate import eur_to_czk_rounded, format_price_display
from apps.core.web_development import WEB_DEV_TIERS, web_dev_prices

NB = '\u00a0'

# Незалежна (порахована вручну) таблиця EUR → Kč при EUR_CZK = 24.5, до 500 Kč, половина вгору.
# EUR-межі тарифів беремо з того ж джерела, що й сайт (web_development.WEB_DEV_TIERS),
# тож зміна цін (напр. e-shop 1 600 → 1 400 €, №28/42) не ламає тести, поки сума є в таблиці.
EUR_TO_CZK = {
    400: 10000,     # 9 800
    700: 17000,     # 17 150
    1000: 24500,    # 24 500
    1400: 34500,    # 34 300
    1600: 39000,    # 39 200
    2800: 68500,    # 68 600
    8000: 196000,   # 196 000
}


def _expected_czk(eur):
    if eur not in EUR_TO_CZK:
        raise AssertionError(f'{eur} € is not in EUR_TO_CZK; add its hand-checked Kč value to the test table')
    return EUR_TO_CZK[eur]


EXPECTED_CZK = {key: (_expected_czk(low), _expected_czk(high)) for key, low, high in WEB_DEV_TIERS}


def _cs_amount(czk):
    return f'{czk:,}'.replace(',', NB)


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
        shop_lo, shop_hi = EXPECTED_CZK['shop']
        self.assertEqual(cs['shop']['czk'], f'≈{NB}{_cs_amount(shop_lo)}–{_cs_amount(shop_hi)}{NB}Kč')
        en = web_dev_prices('en')
        self.assertEqual(en['shop']['czk'], f'≈{NB}CZK{NB}{shop_lo:,}–{shop_hi:,}')


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
        for key in ('landing', 'corporate', 'shop'):  # admin.html «od …»
            self.assertIn(f'≈{NB}{_cs_amount(EXPECTED_CZK[key][0])}{NB}Kč', spans, key)
        self.assertFalse(any('9' + NB + '800' in s for s in spans))

    def test_en_page_czk_values(self):
        spans = self._czk_spans('/en/web-development/')
        self.assertTrue(spans)
        for key, (lo, hi) in EXPECTED_CZK.items():
            self.assertIn(f'≈{NB}CZK{NB}{lo:,}–{hi:,}', spans, key)
