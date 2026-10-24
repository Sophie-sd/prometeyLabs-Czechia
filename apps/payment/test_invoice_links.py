"""Block 4 (pre-Ads launch): payment link from an invoice, purpose / documents / unit /
contract line / methods / EN success text. KeyCRM and e-mail are not involved."""
import io
import re
import shutil
import tempfile
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .admin import PaymentLinkAdminForm
from .invoice_admin import InvoiceAdminForm
from .invoice_links import create_payment_link_from_invoice
from .invoice_models import Invoice, InvoiceItem
from .invoice_pdf import generate_invoice_pdf_bytes, render_invoice_html
from .models import PaymentLink, PaymentLinkFile, PaymentMethod, PaymentText
from .texts import get_texts
from .tests import make_methods

MEDIA = tempfile.mkdtemp(prefix='cz-pay-tests-')


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(data)).pages)


def squash(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


@override_settings(MEDIA_ROOT=MEDIA)
class InvoiceLinkTestsBase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.sepa, self.swift_usd, self.paypal_usd = make_methods()
        self.swift_eur = PaymentMethod.objects.create(
            name='SWIFT EUR', method_type=PaymentMethod.MethodType.SWIFT_EUR, currency='EUR',
            beneficiary='Sofiia Dmytrenko', iban='LT00 0000', swift_bic='REVOLT21', bank_name='Revolut',
        )
        self.admin = get_user_model().objects.create_superuser('admin4', 'a4@example.com', 'pass12345')

    def invoice(self, lang='en', cur='USD', methods=None, contract_number='C-7',
                contract_date=date(2026, 10, 1), unit=''):
        inv = Invoice.objects.create(
            invoice_date=date(2026, 10, 22), client_name='Example s.r.o.', client_tax_id='12345678',
            client_address='Main St 1, Prague', client_country='Czechia', client_email='client@example.com',
            contract_number=contract_number, contract_date=contract_date,
            language=lang, currency=cur, purpose_service='website development',
        )
        inv.payment_methods.set(methods or ([self.swift_usd, self.paypal_usd] if cur == 'USD' else [self.sepa]))
        InvoiceItem.objects.create(invoice=inv, position=1, title='Website development',
                                   quantity=2, price=Decimal('617.25'), unit=unit)
        inv.recalculate_total()
        inv.freeze_snapshots()
        inv.refresh_from_db()
        return inv


class CreateLinkFromInvoiceTests(InvoiceLinkTestsBase):
    def test_link_prefilled_from_invoice_with_pdf(self):
        inv = self.invoice('en', 'USD')
        link, created = create_payment_link_from_invoice(inv)
        self.assertTrue(created)
        self.assertEqual(link.invoice_id, inv.pk)
        self.assertEqual(link.amount, Decimal('1234.50'))
        self.assertEqual(link.amount, inv.total_amount)
        self.assertEqual(link.currency, 'USD')
        self.assertEqual(link.language, 'en')
        self.assertEqual(link.client_name, 'Example s.r.o.')
        self.assertEqual(link.client_email, 'client@example.com')
        self.assertEqual(set(link.payment_methods.all()), {self.swift_usd, self.paypal_usd})
        self.assertEqual(link.payment_purpose(), inv.payment_purpose())
        files = list(link.attached_files.all())
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].file_type, PaymentLinkFile.FileType.INVOICE)
        self.assertTrue(files[0].file.read().startswith(b'%PDF'))
        self.assertEqual(files[0].public_name(get_texts('en')), 'Invoice')

    def test_second_call_reuses_link_no_duplicate(self):
        inv = self.invoice('cs', 'EUR')
        first, created1 = create_payment_link_from_invoice(inv)
        second, created2 = create_payment_link_from_invoice(inv)
        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(PaymentLink.objects.filter(invoice=inv).count(), 1)
        self.assertEqual(PaymentLinkFile.objects.filter(payment_link=first).count(), 1)

    def test_only_methods_in_invoice_currency(self):
        inv = self.invoice('en', 'USD', methods=[self.swift_usd])
        link, _ = create_payment_link_from_invoice(inv)
        self.assertEqual(list(link.payment_methods.all()), [self.swift_usd])

    def test_admin_button_creates_link_and_redirects(self):
        self.client.force_login(self.admin)
        inv = self.invoice('cs', 'EUR')
        change = self.client.get(reverse('admin:payment_invoice_change', args=[inv.pk]))
        self.assertContains(change, 'Створити платіжне посилання з рахунку')
        url = reverse('admin:payment_invoice_create_payment_link', args=[inv.pk])
        self.assertContains(change, f'action="{url}"')
        self.assertContains(change, 'form="invoice-create-link-form"')
        # GET never creates anything
        self.client.get(url)
        self.assertFalse(PaymentLink.objects.filter(invoice=inv).exists())
        response = self.client.post(url)
        link = PaymentLink.objects.get(invoice=inv)
        self.assertRedirects(response, reverse('admin:payment_paymentlink_change', args=[link.pk]),
                             fetch_redirect_response=False)
        self.client.post(url)
        self.assertEqual(PaymentLink.objects.filter(invoice=inv).count(), 1)
        change = self.client.get(reverse('admin:payment_invoice_change', args=[inv.pk]))
        self.assertContains(change, 'Відкрити платіжне посилання')

    def test_admin_bulk_action(self):
        self.client.force_login(self.admin)
        a, b = self.invoice('cs', 'EUR'), self.invoice('en', 'USD')
        self.client.post(reverse('admin:payment_invoice_changelist'), {
            'action': 'create_payment_links_action', '_selected_action': [a.pk, b.pk],
        })
        self.assertEqual(PaymentLink.objects.filter(invoice__in=[a, b]).count(), 2)


class AmountLockedTests(InvoiceLinkTestsBase):
    def setUp(self):
        super().setUp()
        self.inv = self.invoice('en', 'USD')
        self.link, _ = create_payment_link_from_invoice(self.inv)

    def _post_data(self, **over):
        data = {
            'client_name': self.link.client_name, 'client_email': self.link.client_email or '',
            'language': 'en', 'description': self.link.description,
            'currency': 'USD', 'amount': '1234.50',
            'payment_methods': [self.swift_usd.pk], 'status': 'new', 'duration_minutes': 0,
        }
        data.update(over)
        return data

    def test_form_fields_readonly(self):
        form = PaymentLinkAdminForm(instance=self.link)
        self.assertTrue(form.fields['amount'].disabled)
        self.assertTrue(form.fields['currency'].disabled)
        self.assertTrue(form.fields['description'].disabled)

    def test_form_rejects_changed_amount_and_currency(self):
        form = PaymentLinkAdminForm(data=self._post_data(amount='1.00'), instance=self.link)
        self.assertFalse(form.is_valid())
        form = PaymentLinkAdminForm(data=self._post_data(currency='EUR', payment_methods=[self.sepa.pk]),
                                    instance=self.link)
        self.assertFalse(form.is_valid())
        form = PaymentLinkAdminForm(data=self._post_data(), instance=self.link)
        self.assertTrue(form.is_valid(), form.errors)

    def test_admin_post_cannot_change_amount(self):
        self.client.force_login(self.admin)
        url = reverse('admin:payment_paymentlink_change', args=[self.link.pk])
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, f'№{self.inv.number}')
        self.client.post(url, self._post_data(amount='1.00'))
        self.link.refresh_from_db()
        self.assertEqual(self.link.amount, Decimal('1234.50'))

    def test_model_save_and_clean_enforce_invoice_amount(self):
        from django.core.exceptions import ValidationError
        self.link.amount = Decimal('5.00')
        with self.assertRaises(ValidationError):
            self.link.full_clean(exclude=['final_amount_uah'])
        self.link.save()
        self.link.refresh_from_db()
        self.assertEqual(self.link.amount, self.inv.total_amount)

    def test_plain_link_amount_still_editable(self):
        plain = PaymentLink.objects.create(client_name='X', amount=Decimal('10'), currency='USD', language='en')
        form = PaymentLinkAdminForm(instance=plain)
        self.assertFalse(form.fields['amount'].disabled)


class PurposeTests(InvoiceLinkTestsBase):
    def test_en_wording(self):
        inv = self.invoice('en', 'USD')
        self.assertEqual(inv.payment_purpose(),
                         f'Payment for website development by the invoice № {inv.number} from 22.10.2026')

    def test_cs_wording(self):
        inv = self.invoice('cs', 'EUR')
        self.assertEqual(inv.payment_purpose(),
                         f'Platba za website development dle faktury č. {inv.number} ze dne 22.10.2026')

    def test_purpose_identical_in_pdf_and_page(self):
        for lang, cur in (('en', 'USD'), ('cs', 'EUR')):
            with self.subTest(lang=lang):
                inv = self.invoice(lang, cur)
                purpose = inv.payment_purpose()
                link, _ = create_payment_link_from_invoice(inv)
                # PDF attached to the link + freshly rendered HTML
                self.assertIn(purpose, render_invoice_html(inv))
                attached = link.attached_files.get().file.read()
                self.assertIn(squash(purpose), squash(pdf_text(attached)))
                # page after consent
                with translation.override(lang):
                    consent = reverse('payment:record_consent', kwargs={'unique_id': link.unique_id})
                    page = reverse('payment:payment_page', kwargs={'unique_id': link.unique_id})
                self.client.post(consent, {'withdrawal_waiver': '1', 'data_consent': '1'})
                html = self.client.get(page).content.decode()
                self.assertIn(purpose, html)
                # admin description edit must not change what the client sees
                PaymentLink.objects.filter(pk=link.pk).update(description='something else')
                html = self.client.get(page).content.decode()
                self.assertIn(purpose, html)
                self.assertNotIn('something else', html)


class DocumentNamesTests(InvoiceLinkTestsBase):
    def test_document_labels_locked(self):
        PaymentText.objects.update_or_create(key='doc_invoice', defaults={'text_cs': 'Faktúra', 'text_en': 'Bill'})
        PaymentText.objects.update_or_create(key='doc_contract', defaults={'text_cs': 'Dohoda', 'text_en': 'Agreement'})
        cs, en = get_texts('cs'), get_texts('en')
        self.assertEqual((cs['doc_invoice'], cs['doc_contract']), ('Faktura', 'Smlouva'))
        self.assertEqual((en['doc_invoice'], en['doc_contract']), ('Invoice', 'Contract'))

    def test_page_shows_faktura_invoice_smlouva_contract(self):
        from django.core.files.base import ContentFile
        for lang, cur, inv_label, contract_label in (('cs', 'EUR', 'Faktura', 'Smlouva'),
                                                     ('en', 'USD', 'Invoice', 'Contract')):
            with self.subTest(lang=lang):
                link, _ = create_payment_link_from_invoice(self.invoice(lang, cur))
                f = PaymentLinkFile(payment_link=link, file_type=PaymentLinkFile.FileType.CONTRACT,
                                    name='Договір_старий')
                f.file.save('contract.pdf', ContentFile(b'%PDF-1.4'), save=True)
                with translation.override(lang):
                    page = reverse('payment:payment_page', kwargs={'unique_id': link.unique_id})
                html = self.client.get(page).content.decode()
                self.assertRegex(html, rf'>\s*{inv_label}\s*<')
                self.assertRegex(html, rf'>\s*{contract_label}\s*<')
                self.assertNotIn('Договір_старий', html)


class UnitColumnTests(InvoiceLinkTestsBase):
    def test_pdf_unit_is_service_even_with_typo(self):
        PaymentText.objects.update_or_create(key='pdf_unit_default', defaults={'text_cs': 'sllužba', 'text_en': 'servise'})
        for lang, cur, unit in (('cs', 'EUR', 'služba'), ('en', 'USD', 'service')):
            with self.subTest(lang=lang):
                inv = self.invoice(lang, cur, unit='sllužba')
                html = render_invoice_html(inv)
                self.assertIn(unit, html)
                self.assertNotIn('sllužba', html)
                self.assertNotIn('servise', html)
                self.assertIn(unit, pdf_text(generate_invoice_pdf_bytes(inv)))

    def test_unit_hidden_in_admin_form(self):
        self.client.force_login(self.admin)
        html = self.client.get(reverse('admin:payment_invoice_add')).content.decode()
        self.assertNotIn('-unit"', html)
        self.assertNotIn('Од.', html)
        from .invoice_models import InvoiceItem as Item
        self.assertIn('unit', [f.name for f in Item._meta.get_fields()])  # column kept


class ContractLineTests(InvoiceLinkTestsBase):
    def test_no_contract_line_without_number(self):
        for number in ('', '-', '—', ' . '):
            for lang, cur, word in (('cs', 'EUR', 'Smlouva'), ('en', 'USD', 'Contract')):
                with self.subTest(number=number, lang=lang):
                    inv = self.invoice(lang, cur, contract_number=number, contract_date=None)
                    self.assertEqual(inv.contract_line(), '')
                    html = render_invoice_html(inv)
                    self.assertNotIn(word, re.sub(r'<style.*?</style>', '', html, flags=re.S))
                    self.assertNotIn('*', re.sub(r'<style.*?</style>', '', html, flags=re.S))
                    self.assertNotIn(word, pdf_text(generate_invoice_pdf_bytes(inv)))

    def test_date_without_number_not_printed(self):
        inv = self.invoice('en', 'USD', contract_number='-', contract_date=date(2026, 10, 1))
        self.assertEqual(inv.contract_line(), '')
        self.assertNotIn('01.10.2026', render_invoice_html(inv))

    def test_number_with_and_without_date(self):
        inv = self.invoice('cs', 'EUR', contract_number='C-7', contract_date=date(2026, 10, 1))
        self.assertIn('C-7', inv.contract_line())
        self.assertIn('01.10.2026', inv.contract_line())
        inv = self.invoice('en', 'USD', contract_number='C-8', contract_date=None)
        self.assertEqual(inv.contract_line(), 'Contract No. C-8')
        self.assertIn('Contract No. C-8', pdf_text(generate_invoice_pdf_bytes(inv)))

    def _form_data(self, **over):
        data = {
            'language': 'en', 'currency': 'USD', 'payment_methods': [self.swift_usd.pk],
            'client_name': 'Example s.r.o.', 'client_tax_id': '', 'client_vat_id': '',
            'client_address': 'Main St 1', 'client_country': 'Czechia', 'client_email': '',
            'invoice_date': '2026-10-22', 'valid_until': '',
            'contract_number': '', 'contract_date': '', 'purpose_service': '',
        }
        data.update(over)
        return data

    def test_admin_form_contract_optional_and_date_alone_rejected(self):
        self.assertTrue(InvoiceAdminForm(data=self._form_data()).is_valid())
        form = InvoiceAdminForm(data=self._form_data(contract_number='-'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['contract_number'], '')
        form = InvoiceAdminForm(data=self._form_data(contract_date='2026-10-01'))
        self.assertFalse(form.is_valid())
        self.assertIn('contract_date', form.errors)


class MethodNamesTests(InvoiceLinkTestsBase):
    DUP = re.compile(r'SWIFT EUR\s*·|·\s*SWIFT \(EUR\)|\(EUR\)\s*·\s*EUR')

    def test_str_is_name_only(self):
        self.assertEqual(str(self.swift_eur), 'SWIFT EUR')

    def test_admin_pages_have_no_duplicated_method_label(self):
        self.client.force_login(self.admin)
        inv = self.invoice('cs', 'EUR', methods=[self.swift_eur, self.sepa])
        link, _ = create_payment_link_from_invoice(inv)
        for url in (reverse('admin:payment_invoice_add'),
                    reverse('admin:payment_invoice_change', args=[inv.pk]),
                    reverse('admin:payment_paymentlink_add'),
                    reverse('admin:payment_paymentlink_change', args=[link.pk])):
            html = self.client.get(url).content.decode()
            self.assertIn('SWIFT EUR', html, url)
            self.assertIsNone(self.DUP.search(html), url)

    def test_public_page_has_no_duplicated_method_label(self):
        inv = self.invoice('en', 'USD')
        link, _ = create_payment_link_from_invoice(inv)
        with translation.override('en'):
            consent = reverse('payment:record_consent', kwargs={'unique_id': link.unique_id})
            page = reverse('payment:payment_page', kwargs={'unique_id': link.unique_id})
        self.client.post(consent, {'withdrawal_waiver': '1', 'data_consent': '1'})
        html = self.client.get(page).content.decode()
        self.assertNotRegex(html, r'SWIFT USD\s*·|·\s*SWIFT \(USD\)|\(USD\)\s*·\s*USD')


class SuccessAndConsentTextTests(InvoiceLinkTestsBase):
    def test_en_success_page_confirmation_sentence(self):
        link = PaymentLink.objects.create(client_name='X', amount=Decimal('10'), currency='USD', language='en')
        with translation.override('en'):
            url = reverse('payment:payment_success', kwargs={'unique_id': link.unique_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'We have already received the confirmation.')


class TextMigration0017Tests(InvoiceLinkTestsBase):
    def test_updates_only_untouched_defaults(self):
        import importlib
        from django.apps import apps as global_apps
        mig = importlib.import_module('apps.payment.migrations.0017_cz_texts_invoice_link')
        PaymentText.objects.update_or_create(key='purpose_template', defaults={
            'text_cs': 'Platba za {service} dle faktury č. {number} ze dne {date}',
            'text_en': 'Payment for {service} under invoice No. {number} dated {date}'})
        PaymentText.objects.update_or_create(key='success_text', defaults={
            'text_cs': 'Vlastní text', 'text_en': 'Custom EN success'})
        PaymentText.objects.update_or_create(key='pdf_unit_default', defaults={
            'text_cs': 'sllužba', 'text_en': 'service'})
        PaymentText.objects.filter(key='pdf_contract_line_nodate').delete()
        mig.forwards(global_apps, None)
        self.assertEqual(PaymentText.objects.get(key='purpose_template').text_en,
                         'Payment for {service} by the invoice № {number} from {date}')
        self.assertEqual(PaymentText.objects.get(key='success_text').text_en, 'Custom EN success')
        self.assertEqual(PaymentText.objects.get(key='success_text').text_cs, 'Vlastní text')
        self.assertEqual(PaymentText.objects.get(key='pdf_unit_default').text_cs, 'služba')
        self.assertTrue(PaymentText.objects.filter(key='pdf_contract_line_nodate').exists())

    def test_locked_texts_readonly_in_admin(self):
        self.client.force_login(self.admin)
        get_texts('cs')  # seed rows
        obj, _ = PaymentText.objects.get_or_create(key='doc_invoice', defaults={'text_cs': 'Faktura', 'text_en': 'Invoice'})
        html = self.client.get(reverse('admin:payment_paymenttext_change', args=[obj.pk])).content.decode()
        self.assertNotIn('name="text_cs"', html)
        other, _ = PaymentText.objects.get_or_create(key='questions_link', defaults={'text_cs': 'a', 'text_en': 'b'})
        html = self.client.get(reverse('admin:payment_paymenttext_change', args=[other.pk])).content.decode()
        self.assertIn('name="text_cs"', html)
