import io
import re
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .amount_words import amount_in_words
from .invoice_admin import InvoiceAdminForm
from .invoice_models import Invoice, InvoiceItem
from .invoice_pdf import generate_invoice_pdf_bytes, render_invoice_html
from .models import PaymentLink, PaymentMethod, PaymentSettings, PaymentText
from .admin import PaymentLinkAdminForm

CYRILLIC = re.compile(r'[\u0400-\u04FF]')
FORBIDDEN = ('UAH', 'грн', '₴', 'Apple Pay', 'Google Pay', 'Monobank',
             'Přejít k platbě', 'Nebo zaplaťte online', 'Or pay online',
             'Calculate Proposal', 'Courses')


def make_methods():
    sepa = PaymentMethod.objects.create(
        name='Wise SEPA', method_type=PaymentMethod.MethodType.SEPA_EUR,
        currency='EUR', beneficiary='Sofiia Dmytrenko', iban='BE00 0000 0000 0000',
        swift_bic='TRWIBEB1XXX', bank_name='Wise Europe SA',
        beneficiary_address='Rue du Trône 100, Brussels', note_cs='Poznámka CS', note_en='Note EN',
    )
    swift_usd = PaymentMethod.objects.create(
        name='SWIFT USD', method_type=PaymentMethod.MethodType.SWIFT_USD,
        currency='USD', beneficiary='Sofiia Dmytrenko', iban='US-ACC-123',
        swift_bic='CMFGUS33', bank_name='Community Federal Savings Bank',
    )
    paypal_usd = PaymentMethod.objects.create(
        name='PayPal USD', method_type=PaymentMethod.MethodType.PAYPAL,
        currency='USD', paypal_email='pay@example.com', paypal_url='https://paypal.me/example',
    )
    return sepa, swift_usd, paypal_usd


def assert_clean_public_text(testcase, text, where):
    found = CYRILLIC.findall(text)
    testcase.assertFalse(found, f'Cyrillic in {where}: {"".join(found)[:80]}')
    for bad in FORBIDDEN:
        testcase.assertNotIn(bad, text, f'{bad!r} found in {where}')


class AmountWordsTests(TestCase):
    def test_english(self):
        self.assertEqual(amount_in_words(Decimal('1234.50'), 'EUR', 'en'),
                         'One thousand two hundred thirty-four euros and 50 cents')
        self.assertEqual(amount_in_words(Decimal('1.01'), 'USD', 'en'), 'One dollar and 01 cent')

    def test_czech_grammar(self):
        cases = {
            ('1', 'EUR'): 'Jedno euro a 00 centů',
            ('2', 'EUR'): 'Dvě eura a 00 centů',
            ('5', 'EUR'): 'Pět eur a 00 centů',
            ('21', 'EUR'): 'Dvacet jedna eur a 00 centů',
            ('22.02', 'EUR'): 'Dvacet dvě eura a 02 centy',
            ('1234.50', 'EUR'): 'Jeden tisíc dvě stě třicet čtyři eura a 50 centů',
            ('1', 'USD'): 'Jeden dolar a 00 centů',
            ('2', 'USD'): 'Dva dolary a 00 centů',
            ('2500', 'USD'): 'Dva tisíce pět set dolarů a 00 centů',
            ('1001', 'USD'): 'Jeden tisíc jedna dolarů a 00 centů',
            ('12.01', 'USD'): 'Dvanáct dolarů a 01 cent',
        }
        for (amount, cur), expected in cases.items():
            self.assertEqual(amount_in_words(Decimal(amount), cur, 'cs'), expected)


class PaymentMethodValidationTests(TestCase):
    def test_type_currency_must_match(self):
        m = PaymentMethod(name='x', method_type=PaymentMethod.MethodType.SWIFT_USD, currency='EUR',
                          beneficiary='B', iban='I', swift_bic='S')
        with self.assertRaises(Exception):
            m.full_clean()
        m.currency = 'USD'
        m.full_clean()


class InvoiceTests(TestCase):
    def setUp(self):
        self.sepa, self.swift_usd, self.paypal_usd = make_methods()

    def _form_data(self, **over):
        data = {
            'language': 'en', 'currency': 'USD',
            'payment_methods': [self.swift_usd.pk],
            'client_name': 'Example s.r.o.', 'client_tax_id': '12345678', 'client_vat_id': '',
            'client_address': 'Main St 1, Prague', 'client_country': 'Czechia',
            'client_email': 'client@example.com',
            'invoice_date': '2026-10-22', 'valid_until': '',
            'contract_number': 'C-7', 'contract_date': '2026-10-01', 'purpose_service': '',
        }
        data.update(over)
        return data

    def test_usd_invoice_rejects_eur_method(self):
        form = InvoiceAdminForm(data=self._form_data(payment_methods=[self.sepa.pk]))
        self.assertFalse(form.is_valid())
        self.assertIn('payment_methods', form.errors)

    def test_usd_invoice_accepts_usd_methods(self):
        form = InvoiceAdminForm(data=self._form_data(payment_methods=[self.swift_usd.pk, self.paypal_usd.pk]))
        self.assertTrue(form.is_valid(), form.errors)

    def test_methods_required(self):
        form = InvoiceAdminForm(data=self._form_data(payment_methods=[]))
        self.assertFalse(form.is_valid())

    def test_due_date_default_plus_3_days(self):
        form = InvoiceAdminForm(data=self._form_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['valid_until'], date(2026, 10, 25))
        inv = Invoice.objects.create(
            invoice_date=date(2026, 10, 22), client_name='A', contract_number='1',
            contract_date=date(2026, 10, 1), language='cs', currency='EUR',
        )
        self.assertEqual(inv.valid_until, date(2026, 10, 25))
        self.assertEqual(InvoiceAdminForm().fields['valid_until'].initial, date.today() + timedelta(days=3))

    def test_due_date_editable(self):
        form = InvoiceAdminForm(data=self._form_data(valid_until='2026-11-05'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['valid_until'], date(2026, 11, 5))
        inv = Invoice.objects.create(
            invoice_date=date(2026, 10, 22), valid_until=date(2026, 11, 5), client_name='A',
            contract_number='1', contract_date=date(2026, 10, 1), language='cs', currency='EUR',
        )
        inv.save()
        self.assertEqual(inv.valid_until, date(2026, 11, 5))

    def _invoice(self, lang, cur, methods):
        inv = Invoice.objects.create(
            invoice_date=date(2026, 10, 22), client_name='Example s.r.o.', client_tax_id='12345678',
            client_vat_id='CZ12345678', client_address='Main St 1, Prague', client_country='Czechia',
            client_email='client@example.com', contract_number='C-7', contract_date=date(2026, 10, 1),
            language=lang, currency=cur, purpose_service='website development',
        )
        inv.payment_methods.set(methods)
        InvoiceItem.objects.create(invoice=inv, position=1, title='Website development', quantity=1, price=Decimal('1234.50'))
        inv.recalculate_total()
        inv.freeze_snapshots()
        return inv

    def test_purpose_text_en_and_cs(self):
        en = self._invoice('en', 'USD', [self.swift_usd])
        self.assertEqual(en.payment_purpose(),
                         f'Payment for website development by the invoice № {en.number} from 22.10.2026')
        cs = self._invoice('cs', 'EUR', [self.sepa])
        self.assertEqual(cs.payment_purpose(),
                         f'Platba za website development dle faktury č. {cs.number} ze dne 22.10.2026')

    def test_purpose_falls_back_to_first_item(self):
        inv = self._invoice('en', 'USD', [self.swift_usd])
        inv.purpose_service = ''
        inv.save()
        self.assertIn('Payment for Website development by the invoice №', inv.payment_purpose())

    def test_pdf_cs_eur_and_en_usd_have_no_ukrainian(self):
        from pypdf import PdfReader
        for lang, cur, methods, title, note in (
            ('cs', 'EUR', [self.sepa], 'Faktura / Akt o poskytnutých službách', 'DPH není účtována.'),
            ('en', 'USD', [self.swift_usd, self.paypal_usd], 'Invoice / Act of services rendered', 'VAT is not charged.'),
        ):
            inv = self._invoice(lang, cur, methods)
            html = render_invoice_html(inv)
            self.assertIn(title, html)
            self.assertIn(note, html)
            self.assertIn(cur, html)
            assert_clean_public_text(self, re.sub(r'<style.*?</style>', '', html, flags=re.S), f'PDF html {lang}')
            pdf = generate_invoice_pdf_bytes(inv)
            text = '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(pdf)).pages)
            assert_clean_public_text(self, text, f'PDF text {lang}')
            self.assertIn(cur, text)
            self.assertEqual(len(PdfReader(io.BytesIO(pdf)).pages), 1, f'PDF {lang} fits one page')
            if lang == 'en':
                # «№» only in the bank purpose wording (block 4c), rendered by NotoSans
                self.assertNotIn('№', html.replace(inv.payment_purpose(), ''))
                self.assertNotIn('Executor', html + text)
                self.assertIn('SUPPLIER', text.upper())
                self.assertIn('signature', text)
                self.assertIn('by the invoice №', ' '.join(text.split()))
            else:
                self.assertIn('podpis', text)

    def test_pdf_prints_each_method(self):
        inv = self._invoice('en', 'USD', [self.swift_usd, self.paypal_usd])
        html = render_invoice_html(inv)
        self.assertIn('CMFGUS33', html)
        self.assertIn('pay@example.com', html)
        self.assertIn("In words", html)

    def test_legacy_invoice_pdf_not_regenerated(self):
        from .invoice_pdf import LegacyInvoiceError
        inv = Invoice.objects.create(
            invoice_date=date(2026, 1, 1), client_name='Old', contract_number='1',
            contract_date=date(2026, 1, 1), language='', currency='',
        )
        with self.assertRaises(LegacyInvoiceError):
            generate_invoice_pdf_bytes(inv)


class PaymentPageTests(TestCase):
    def setUp(self):
        self.sepa, self.swift_usd, self.paypal_usd = make_methods()
        s = PaymentSettings.get_solo()
        s.save()
        self.link = PaymentLink.objects.create(
            client_name='Test Client', client_email='client@example.com',
            description='Website development, invoice 85', amount=Decimal('1234.50'),
            currency='EUR', language='cs',
        )
        self.link.payment_methods.set([self.sepa])
        self.usd_link = PaymentLink.objects.create(
            client_name='US Client', description='Web app', amount=Decimal('2500.00'),
            currency='USD', language='en',
        )
        self.usd_link.payment_methods.set([self.swift_usd, self.paypal_usd])

    def _page(self, link, lang):
        with translation.override(lang):
            url = reverse('payment:payment_page', kwargs={'unique_id': link.unique_id})
        return url, self.client.get(url)

    def _consent(self, link, lang, data=None):
        with translation.override(lang):
            url = reverse('payment:record_consent', kwargs={'unique_id': link.unique_id})
        return self.client.post(url, data if data is not None else {'withdrawal_waiver': '1', 'data_consent': '1'})

    def test_checkboxes_present_not_prechecked_and_details_hidden(self):
        for link, lang in ((self.link, 'cs'), (self.usd_link, 'en')):
            _url, response = self._page(link, lang)
            self.assertEqual(response.status_code, 200)
            html = response.content.decode()
            self.assertIn('name="withdrawal_waiver"', html)
            self.assertIn('name="data_consent"', html)
            self.assertNotIn('checked', html)
            self.assertNotIn('ec.europa.eu/consumers/odr', html)
            # details are NOT revealed before consent
            self.assertNotIn('BE00 0000 0000 0000', html)
            self.assertNotIn('CMFGUS33', html)
            self.assertNotIn('paypal.me', html)
            # before consent: no "How to pay" block, one action + small questions link
            self.assertNotIn('pay-block--howto', html)
            self.assertNotIn('Jak zaplatit', html)
            self.assertNotIn('How to pay', html)
            self.assertEqual(html.count('type="submit"'), 1)
            self.assertIn('Máte otázky? Napište nám' if lang == 'cs' else 'Questions? Write to us', html)
            self.assertIn('href="mailto:info@prometeylabs.com"', html)
            self.assertNotIn('Executor', html)
            assert_clean_public_text(self, html, f'payment page {lang} before consent')

    def test_consent_missing_keeps_details_hidden(self):
        response = self._consent(self.link, 'cs', {'withdrawal_waiver': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('consent=missing', response['Location'])
        self.link.refresh_from_db()
        self.assertIsNone(self.link.withdrawal_waiver_accepted_at)
        self.assertIsNone(self.link.data_consent_accepted_at)
        _url, response = self._page(self.link, 'cs')
        self.assertNotIn('BE00 0000 0000 0000', response.content.decode())

    def test_consent_reveals_details_cs(self):
        response = self._consent(self.link, 'cs')
        self.assertEqual(response.status_code, 302)
        self.link.refresh_from_db()
        self.assertIsNotNone(self.link.withdrawal_waiver_accepted_at)
        self.assertIsNotNone(self.link.data_consent_accepted_ip)
        _url, response = self._page(self.link, 'cs')
        html = response.content.decode()
        self.assertIn('BE00 0000 0000 0000', html)
        self.assertIn('Kopírovat údaje SEPA', html)
        self.assertIn('data-copy-done="Zkopírováno ✓"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('Jak zaplatit', html)
        # no nested frames: details are <dl> rows; amount + purpose are the first rows
        self.assertIn('<dl class="pay-dl">', html)
        self.assertNotIn('req-list', html)
        dl = html[html.index('<dl class="pay-dl">'):]
        self.assertLess(dl.index('pay-row--amount'), dl.index('Website development, invoice 85'))
        self.assertLess(dl.index('Website development, invoice 85'), dl.index('BE00 0000 0000 0000'))
        self.assertIn('1\u00a0234,50', html)
        self.assertIn('EUR', html)
        self.assertIn('Poznámka CS', html)
        self.assertIn('href="https://prometeylabs.cz"', html)
        self.assertNotIn('href="https://prometeylabs.com', html)
        assert_clean_public_text(self, html, 'payment page cs after consent')

    def test_consent_reveals_details_en_with_paypal_button(self):
        self._consent(self.usd_link, 'en')
        url, response = self._page(self.usd_link, 'en')
        self.assertTrue(url.startswith('/en/'))
        html = response.content.decode()
        self.assertIn('CMFGUS33', html)
        self.assertIn('Copy SWIFT details', html)
        self.assertIn('data-copy-done="Copied ✓"', html)
        self.assertIn('Pay with PayPal', html)
        self.assertIn('Supplier', html)
        self.assertNotIn('Executor', html)
        self.assertIn('href="mailto:info@prometeylabs.com"', html)
        self.assertIn('How to pay', html)
        self.assertIn('https://paypal.me/example', html)
        self.assertIn('2,500.00', html)
        self.assertIn('USD', html)
        assert_clean_public_text(self, html, 'payment page en after consent')

    def test_eur_method_not_shown_on_usd_link(self):
        self.usd_link.payment_methods.add(self.sepa)
        self._consent(self.usd_link, 'en')
        _url, response = self._page(self.usd_link, 'en')
        self.assertNotIn('BE00 0000 0000 0000', response.content.decode())

    def test_payment_link_form_currency_validation(self):
        data = {
            'client_name': 'X', 'client_email': '', 'language': 'en', 'description': '',
            'currency': 'USD', 'amount': '10', 'payment_methods': [self.sepa.pk],
            'status': 'new', 'duration_minutes': 0,
        }
        form = PaymentLinkAdminForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('payment_methods', form.errors)
        data['payment_methods'] = [self.swift_usd.pk]
        self.assertTrue(PaymentLinkAdminForm(data=data).is_valid())

    def test_client_path_uses_link_language(self):
        self.assertFalse(self.link.client_path().startswith('/en/'))
        self.assertTrue(self.usd_link.client_path().startswith('/en/'))

    def test_online_payment_removed(self):
        url = reverse('payment:create_invoice', kwargs={'unique_id': self.link.unique_id})
        response = self.client.post(url, {'withdrawal_waiver': '1', 'data_consent': '1'})
        self.assertEqual(response.status_code, 410)
        self.link.refresh_from_db()
        self.assertEqual(self.link.monobank_invoice_id, '')

    def test_legacy_uah_link_is_inactive_without_uah(self):
        PaymentLink.objects.filter(pk=self.link.pk).update(currency='UAH')
        _url, response = self._page(self.link, 'cs')
        self.assertEqual(response.status_code, 200)
        assert_clean_public_text(self, response.content.decode(), 'legacy link page')

    def test_texts_are_editable_in_cms(self):
        PaymentText.objects.update_or_create(key='copy_details', defaults={'text_cs': 'Zkopírovat vše', 'text_en': 'Copy all {method} data'})
        PaymentText.objects.update_or_create(key='questions_link', defaults={'text_cs': 'Dotazy?', 'text_en': 'Need help?'})
        _url, response = self._page(self.usd_link, 'en')
        self.assertContains(response, 'Need help?')
        self._consent(self.usd_link, 'en')
        _url, response = self._page(self.usd_link, 'en')
        self.assertContains(response, 'Copy all SWIFT data')

    def test_success_page_has_waiver_text(self):
        url = reverse('payment:payment_success', kwargs={'unique_id': self.link.unique_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '§1824a')
        assert_clean_public_text(self, response.content.decode(), 'success page')

    def test_impressum_in_footer(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertTrue('plf__impressum' in html or 'footer-impressum' in html)
        self.assertNotIn('ec.europa.eu/consumers/odr', html)


class PaymentAdminTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser('admin', 'a@example.com', 'pass12345')
        self.client.force_login(self.user)
        make_methods()

    def test_admin_pages_render(self):
        for name in (
            'admin:payment_paymentlink_changelist', 'admin:payment_paymentlink_add',
            'admin:payment_invoice_changelist', 'admin:payment_invoice_add',
            'admin:payment_paymentmethod_changelist', 'admin:payment_paymentmethod_add',
            'admin:payment_paymenttext_changelist', 'admin:payment_paymentsettings_changelist',
        ):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_acquiring_and_subscriptions_hidden(self):
        html = self.client.get(reverse('admin:payment_paymentlink_add')).content.decode()
        for field in ('use_acquiring', 'exchange_rate', 'final_amount_uah', 'is_subscription',
                      'monobank_invoice_id', 'card_token', 'name="recipient"'):
            self.assertNotIn(field, html)
        self.assertNotIn('is_subscription=1', html)
        self.assertNotIn('Підписк', html)
        inv_html = self.client.get(reverse('admin:payment_invoice_add')).content.decode()
        for word in ('РНОКПП', 'ЄДРПОУ', 'ФОП', 'ТОВ', 'МФО'):
            self.assertNotIn(word, inv_html)

    def test_text_migration_updates_only_untouched_defaults(self):
        import importlib
        mig = importlib.import_module('apps.payment.migrations.0015_cz_texts_design_review')
        from django.apps import apps as global_apps
        PaymentText.objects.update_or_create(key='executor_label', defaults={'text_cs': 'Poskytovatel', 'text_en': 'Executor'})
        PaymentText.objects.update_or_create(key='pdf_signature', defaults={'text_cs': 'Poskytovatel', 'text_en': 'Signed by owner'})
        PaymentText.objects.filter(key='questions_link').delete()
        mig.forwards(global_apps, None)
        self.assertEqual(PaymentText.objects.get(key='executor_label').text_en, 'Supplier')
        self.assertEqual(PaymentText.objects.get(key='pdf_signature').text_en, 'Signed by owner')
        self.assertTrue(PaymentText.objects.filter(key='questions_link').exists())

    def test_payment_texts_seeded(self):
        self.client.get(reverse('admin:payment_paymenttext_changelist'))
        self.assertTrue(PaymentText.objects.filter(key='pdf_footer_note').exists())
