"""
Тести для форм зворотного зв'язку
"""
from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse
from pathlib import Path
import json

from apps.core.models import FormSubmission


def _lead(**extra):
    data = {
        'name': 'Іван Петренко',
        'email': 'ivan@example.com',
        'consent': '1',
        'phone': '+380631234567',
    }
    data.update(extra)
    return data


class FormValidationTests(TestCase):
    """Тести валідації форм"""

    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('form_submit')

    def test_footer_form_with_valid_data(self):
        data = _lead(form_type='footer-consultation')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])
        sub = FormSubmission.objects.latest('id')
        self.assertIsNotNone(sub.consent_at)
        self.assertEqual(sub.email, 'ivan@example.com')

    def test_call_request_form_with_valid_data(self):
        data = _lead(
            form_type='call_request',
            name='Марія Іванівна',
            phone='0631234567',
            email='maria@example.com',
            project_type='eshop',
            budget='500_1500',
            preferred_language='cs',
            messenger_type='telegram',
        )
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])
        sub = FormSubmission.objects.latest('id')
        self.assertEqual(sub.project_type, 'eshop')
        self.assertEqual(sub.budget, '500_1500')
        self.assertEqual(sub.preferred_language, 'cs')
        self.assertEqual(sub.messenger_type, 'telegram')

    def test_contact_form_with_valid_data(self):
        data = _lead(
            form_type='contact',
            name='Петро Сидоренко',
            phone='+380961234567',
            email='petro@example.com',
            message='Мені потрібна консультація',
        )
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertTrue(json_data['success'])

    def test_lead_rejects_missing_consent(self):
        data = _lead(form_type='footer-consultation')
        del data['consent']
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)['success'])

    def test_lead_rejects_missing_email(self):
        data = _lead(form_type='footer-consultation')
        del data['email']
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)['success'])

    def test_lead_phone_optional(self):
        data = _lead(form_type='footer-consultation')
        data['phone'] = ''
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_form_with_invalid_name_short(self):
        data = _lead(form_type='footer-consultation', name='А')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.content)
        self.assertFalse(json_data['success'])
        self.assertIn('jméno', json_data['message'].lower())

    def test_form_with_invalid_name_only_digits(self):
        data = _lead(form_type='footer-consultation', name='12345')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)['success'])

    def test_form_with_invalid_phone_short(self):
        data = _lead(form_type='footer-consultation', phone='123')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.content)
        self.assertFalse(json_data['success'])
        self.assertIn('telefon', json_data['message'].lower())

    def test_form_with_international_phone(self):
        data = _lead(form_type='footer-consultation', phone='+44 20 7946 0958')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_form_with_local_phone_seven_digits(self):
        data = _lead(form_type='footer-consultation', phone='555-1234')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_form_missing_required_fields(self):
        data = {
            'form_type': 'footer-consultation',
            'name': 'Іван Петренко',
            'consent': '1',
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)['success'])

    def test_form_with_special_chars_in_phone(self):
        data = _lead(form_type='footer-consultation', phone='+38 (063) 123-45-67')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_form_with_cyrillic_name(self):
        data = _lead(form_type='footer-consultation', name='Василь')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_form_with_mixed_chars_in_name(self):
        data = _lead(form_type='footer-consultation', name='John Джон')
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_developer_still_requires_phone(self):
        """Developer-модалка поза редизайном — ім'я+телефон."""
        data = {
            'form_type': 'developer',
            'name': 'Тест Курс',
            'phone': '+380631234567',
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_site_request_requires_consent_email_optional(self):
        data = {
            'form_type': 'site_request',
            'name': 'Квіз Клієнт',
            'phone': '+380501112233',
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)

        data['consent'] = '1'
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

        data['email'] = 'not-an-email'
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 400)

        data['email'] = 'quiz@example.com'
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])

    def test_call_request_requires_consent_and_email(self):
        data = {
            'form_type': 'call_request',
            'name': 'Безкоштовний аналіз',
            'phone': '+380671112233',
            'consent': '1',
            'email': 'call@example.com',
        }
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])


class CalculatorTestSubmissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('test_submit')

    def _payload(self, **extra):
        data = {
            'name': 'Calc User',
            'phone': '+380631234567',
            'email': 'calc@example.com',
            'consent': '1',
            'question_1': 'A',
            'question_2': 'A',
            'question_3': 'B',
            'question_4': 'A',
            'question_5': 'A',
        }
        data.update(extra)
        return data

    def test_calculator_rejects_missing_consent(self):
        data = self._payload()
        del data['consent']
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)['success'])

    def test_calculator_allows_missing_email(self):
        data = self._payload()
        del data['email']
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertTrue(body['success'])
        self.assertEqual(body['redirect'], '/thank-you/')

    def test_calculator_rejects_invalid_email(self):
        response = self.client.post(self.url, self._payload(email='not-an-email'))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json.loads(response.content)['success'])

    def test_calculator_redirects_to_thank_you(self):
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertTrue(body['success'])
        self.assertEqual(body['redirect'], '/thank-you/')
        self.assertNotIn('result', body)



class ThankYouRedirectLocaleTests(TestCase):
    """redirect у JSON-відповіді веде на /thank-you/ мовою ліда (cs без префікса, en → /en/)."""

    def tearDown(self):
        from django.conf import settings as dj_settings
        from django.utils import translation
        translation.activate(dj_settings.LANGUAGE_CODE)

    def _post(self, url, **kw):
        response = self.client.post(url, _lead(form_type='contact', message='TEST'), **kw)
        self.assertEqual(response.status_code, 200, response.content)
        return json.loads(response.content)['redirect']

    def test_cs_lead_redirects_to_unprefixed_thank_you(self):
        self.assertEqual(self._post('/forms/submit/'), '/thank-you/')

    def test_en_lead_redirects_to_en_thank_you(self):
        self.assertEqual(self._post('/en/forms/submit/'), '/en/thank-you/')

    def test_unprefixed_endpoint_from_en_page_redirects_to_en(self):
        self.assertEqual(
            self._post('/forms/submit/', HTTP_REFERER='http://testserver/en/contacts/'),
            '/en/thank-you/',
        )

    def test_calculator_cs_and_en(self):
        data = {'name': 'TEST Calc', 'phone': '+420777123456', 'consent': '1', 'question_1': 'A'}
        cs = json.loads(self.client.post('/forms/test/', data).content)['redirect']
        en = json.loads(self.client.post('/en/forms/test/', data).content)['redirect']
        self.assertEqual((cs, en), ('/thank-you/', '/en/thank-you/'))

    def test_honeypot_en_uses_active_language(self):
        response = self.client.post(
            '/en/forms/submit/', _lead(form_type='telegram-bot', honeypot='bot'),
        )
        self.assertEqual(json.loads(response.content)['redirect'], '/en/thank-you/')

    def test_thank_you_pages_exist(self):
        self.assertEqual(self.client.get('/thank-you/').status_code, 200)
        self.assertEqual(self.client.get('/en/thank-you/').status_code, 200)


ROOT = Path(__file__).resolve().parents[3]


class CalculatorMarkupTests(SimpleTestCase):
    def test_email_is_optional_in_calculator_template(self):
        text = (ROOT / 'templates/pages/calculator.html').read_text(encoding='utf-8')
        self.assertIn('email_optional=True', text)

    def test_result_modal_removed_from_modals(self):
        text = (ROOT / 'templates/components/modals.html').read_text(encoding='utf-8')
        self.assertNotIn('test-result-modal', text)
        self.assertNotIn('Результат розрахунку', text)
