"""EUR/Kč switch: default per language, cookie wins, prices follow the calculator rate."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.calculator_estimate import eur_to_czk_rounded
from apps.core.fx import CURRENCY_COOKIE, format_from, format_range

NBSP = '\u00a0'


class CurrencyDefaultTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_czech_page_opens_in_koruna(self):
        html = self.client.get('/').content.decode()
        self.assertIn(f'{eur_to_czk_rounded(400):,}'.replace(',', NBSP), html)
        self.assertNotIn('400–700', html)

    def test_english_page_opens_in_euro(self):
        html = self.client.get('/en/').content.decode()
        self.assertIn(f'400–700{NBSP}€', html)

    def test_cookie_overrides_the_default(self):
        self.client.cookies[CURRENCY_COOKIE] = 'EUR'
        html = self.client.get('/').content.decode()
        self.assertIn(f'400–700{NBSP}€', html)


class CurrencySwitchViewTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_post_sets_cookie_and_returns_to_the_page(self):
        response = self.client.post(
            reverse('set_currency'), {'currency': 'EUR', 'next': '/'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
        self.assertEqual(response.cookies[CURRENCY_COOKIE].value, 'EUR')

    def test_unknown_currency_falls_back_to_the_default(self):
        response = self.client.post(
            reverse('set_currency'), {'currency': 'UAH', 'next': '/'}
        )
        self.assertEqual(response.cookies[CURRENCY_COOKIE].value, 'CZK')

    def test_get_is_rejected(self):
        self.assertEqual(self.client.get(reverse('set_currency')).status_code, 405)


class CurrencyMarkupTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_switch_is_on_home_and_shop(self):
        for path in ('/', '/internet-shop/', '/tvorba-webu/'):
            html = self.client.get(path).content.decode()
            self.assertIn('class="fx-switch', html, path)
            self.assertIn('Kč', html, path)

    def test_shop_quiz_prices_follow_the_switch(self):
        html = self.client.get('/internet-shop/').content.decode()
        self.assertIn(f'data-fx-price-base="{format_from(1400, "CZK")}"', html)
        self.client.cookies[CURRENCY_COOKIE] = 'EUR'
        html = self.client.get('/internet-shop/').content.decode()
        self.assertIn(f'data-fx-price-base="{format_from(1400, "EUR")}"', html)

    def test_rates_match_the_calculator(self):
        """Prices on the pages may never drift from what the calculator mails out."""
        self.assertEqual(
            format_range(400, 700, 'CZK'),
            f'{eur_to_czk_rounded(400):,}'.replace(',', NBSP)
            + '–'
            + f'{eur_to_czk_rounded(700):,}'.replace(',', NBSP)
            + f'{NBSP}Kč',
        )


class CurrencyCssCopyTests(TestCase):
    def test_page_copy_matches_the_component(self):
        """/tvorba-webu/ inlines currency.css instead of linking it — keep the copy in sync."""
        root = settings.BASE_DIR
        component = (root / 'static/css/components/currency.css').read_text(encoding='utf-8').strip()
        page = (root / 'static/css/pages/rozrobka-sajtiv.css').read_text(encoding='utf-8')
        start = page.index('.fx-switch {')
        self.assertIn(component, page[start:])
