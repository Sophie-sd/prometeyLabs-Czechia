from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import PaymentLink, RecipientProfile


class CheckoutConsentTests(TestCase):
    def setUp(self):
        self.recipient = RecipientProfile.objects.create(
            name='Test FOP',
            recipient='FOP Test',
            iban='UA000000000000000000000000000',
            ipn='1234567890',
        )
        self.link = PaymentLink.objects.create(
            client_name='Test Client',
            client_email='client@example.com',
            description='Custom site',
            recipient=self.recipient,
            amount=Decimal('100.00'),
            currency=PaymentLink.Currency.UAH,
            use_acquiring=True,
        )

    def test_payment_page_checkboxes_not_prechecked(self):
        url = reverse('payment:payment_page', kwargs={'unique_id': self.link.unique_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('name="withdrawal_waiver"', html)
        self.assertIn('name="data_consent"', html)
        self.assertNotIn('name="withdrawal_waiver" checked', html)
        self.assertNotIn('name="data_consent" checked', html)
        self.assertNotIn('ec.europa.eu/consumers/odr', html)

    def test_create_invoice_rejects_missing_consents(self):
        url = reverse('payment:create_invoice', kwargs={'unique_id': self.link.unique_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.link.refresh_from_db()
        self.assertIsNone(self.link.withdrawal_waiver_accepted_at)

    def test_record_consent_saves_ip(self):
        self.link.use_acquiring = False
        self.link.save(update_fields=['use_acquiring'])
        url = reverse('payment:record_consent', kwargs={'unique_id': self.link.unique_id})
        response = self.client.post(url, {
            'withdrawal_waiver': '1',
            'data_consent': '1',
        })
        self.assertEqual(response.status_code, 302)
        self.link.refresh_from_db()
        self.assertIsNotNone(self.link.withdrawal_waiver_accepted_at)
        self.assertIsNotNone(self.link.data_consent_accepted_at)

    def test_success_page_has_waiver_text(self):
        url = reverse('payment:payment_success', kwargs={'unique_id': self.link.unique_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '§1824a')

    def test_impressum_in_footer(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        # redesigned footer (Figma) renders the impressum as .plf__impressum
        self.assertTrue('plf__impressum' in html or 'footer-impressum' in html)
        self.assertNotIn('ec.europa.eu/consumers/odr', html)
