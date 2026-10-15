"""EU phone field: server-side validation + E.164 normalisation (mirrors phone-mask-intl.js)."""
import json
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from apps.core.form_handlers import normalize_phone, strip_prefix_only, validate_phone
from apps.core.models import FormSubmission


class NormalizePhoneTests(TestCase):
    def test_valid_numbers(self):
        cases = {
            '+420 777 123 456': '+420777123456',
            '777 123 456': '+420777123456',          # national → +420 default
            '00420777123456': '+420777123456',
            '+49 151 23456789': '+4915123456789',
            '+49 0151 23456789': '+4915123456789',   # DE trunk 0 dropped
            '+48 512 345 678': '+48512345678',
            '+421 905 123 456': '+421905123456',
            '+43 664 1234567': '+436641234567',
            '+44 7911 123456': '+447911123456',
            '+380 63 123 4567': '+380631234567',
        }
        for raw, e164 in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_phone(raw), e164)
                self.assertTrue(validate_phone(raw))

    def test_invalid_numbers(self):
        for raw in ['+420 777 123 45', '+420 777 123 4567', '+48 512 345 67', '+421 905 123',
                    '+49 151', '555-1234', '+999 123456789', '', 'abc']:
            with self.subTest(raw=raw):
                self.assertIsNone(normalize_phone(raw))
                self.assertFalse(validate_phone(raw))

    def test_prefix_only_is_empty(self):
        for raw in ['+420', '+420 ', '+49', '0048']:
            self.assertEqual(strip_prefix_only(raw), '')
        self.assertEqual(strip_prefix_only('+420 777 123 456'), '+420 777 123 456')


@mock.patch('apps.core.views._dispatch_async', lambda *a, **k: None)
class PhoneSubmitTests(TestCase):
    url = reverse('form_submit')

    def _post(self, phone, **extra):
        data = {'form_type': 'contact', 'name': 'Jana', 'phone': phone, 'consent': '1'}
        data.update(extra)
        return self.client.post(self.url, data)

    def test_cz_saved_as_e164(self):
        r = self._post('+420 777 123 456')
        self.assertTrue(json.loads(r.content)['success'])
        self.assertEqual(FormSubmission.objects.latest('id').phone, '+420777123456')

    def test_de_pl_sk_valid(self):
        for raw, e164 in [('+49 151 23456789', '+4915123456789'), ('+48 512 345 678', '+48512345678'),
                          ('+421 905 123 456', '+421905123456')]:
            with self.subTest(raw=raw):
                r = self._post(raw)
                self.assertTrue(json.loads(r.content)['success'])
                self.assertEqual(FormSubmission.objects.latest('id').phone, e164)

    def test_invalid_rejected(self):
        for raw in ['+420 777 12', '+48 512 345 67', '+421 905 12', '+49 15']:
            with self.subTest(raw=raw):
                r = self._post(raw)
                self.assertFalse(json.loads(r.content)['success'])

    def test_prefix_only_with_email_is_ok(self):
        r = self._post('+420', email='jana@example.cz')
        self.assertTrue(json.loads(r.content)['success'])
