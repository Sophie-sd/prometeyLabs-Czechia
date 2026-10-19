"""TZ-генератор: серверна перевірка згоди, gclid/UTM/landing у ліді, ім'я PDF cs/en."""
import json
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import translation

from apps.core.keycrm_service import KeyCRMService
from apps.core.models import FormSubmission


def _tz(**extra):
    data = {
        'name': 'TEST Jan', 'phone': '+420777123456', 'email': 'test@example.com',
        'quiz': json.dumps({'description': 'TEST'}), 'consent': '1',
    }
    data.update(extra)
    return data


@mock.patch('apps.core.tz_views._dispatch_async')
class TzConsentTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_missing_consent_rejected_cs(self, _d):
        data = _tz(); del data['consent']
        r = self.client.post('/forms/tz/', data)
        self.assertEqual(r.status_code, 400)
        body = json.loads(r.content)
        self.assertFalse(body['success'])
        self.assertIn('souhlas', body['message'].lower())
        self.assertFalse(FormSubmission.objects.exists())
        _d.assert_not_called()

    def test_missing_consent_rejected_en(self, _d):
        data = _tz(); del data['consent']
        r = self.client.post('/en/forms/tz/', data)
        self.assertEqual(r.status_code, 400)
        self.assertFalse(FormSubmission.objects.exists())

    def test_with_consent_saves_tracking(self, _d):
        r = self.client.post('/forms/tz/', _tz(
            gclid='TEST-GCLID-TZ', utm_source='google', utm_medium='cpc',
            utm_campaign='cz-tz', utm_term='zadani', utm_content='ad1',
            landing_page='/tz-dlia-saitu/', landing_referrer='https://www.google.com/',
            source_page='/tz-dlia-saitu/',
        ))
        self.assertEqual(r.status_code, 200, r.content)
        sub = FormSubmission.objects.get()
        self.assertIsNotNone(sub.consent_at)
        self.assertEqual(sub.gclid, 'TEST-GCLID-TZ')
        self.assertEqual((sub.utm_source, sub.utm_medium, sub.utm_campaign, sub.utm_term, sub.utm_content),
                         ('google', 'cpc', 'cz-tz', 'zadani', 'ad1'))
        self.assertEqual(sub.extra_data['landing_page'], '/tz-dlia-saitu/')
        self.assertEqual(sub.extra_data['landing_referrer'], 'https://www.google.com/')
        self.assertEqual((sub.extra_data['site'], sub.extra_data['lang']), ('cz', 'cs'))

    @override_settings(KEYCRM_API_KEY='test-key-not-real', KEYCRM_GCLID_FIELD_UUID='')
    @mock.patch('apps.core.keycrm_service.requests.post')
    def test_keycrm_payload_has_tracking(self, post, _d):
        resp = mock.Mock(status_code=201, text=''); resp.json.return_value = {'id': 1}
        post.return_value = resp
        self.client.post('/en/forms/tz/', _tz(
            gclid='TEST-GCLID-TZ', utm_source='google', utm_campaign='cz-tz',
            landing_page='/en/tz-dlia-saitu/',
        ))
        KeyCRMService().create_pipeline_card(FormSubmission.objects.get())
        payload = post.call_args.kwargs['json']
        self.assertEqual(payload['utm_source'], 'google')
        self.assertEqual(payload['utm_campaign'], 'cz-tz')
        for line in ('GCLID: TEST-GCLID-TZ', 'Site: cz', 'Lang: en', 'Form: tz_generator'):
            self.assertIn(line, payload['manager_comment'])
        self.assertIn('/en/tz-dlia-saitu/', payload['manager_comment'])


@mock.patch('apps.core.tz_pdf.generate_tz_pdf_bytes', return_value=b'%PDF-1.4 TEST')
class TzPdfFilenameTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def _sub(self, token, lang=None):
        extra = {'pdf_token': token}
        if lang:
            extra['lang'] = lang
        return FormSubmission.objects.create(form_type='tz_generator', name='TEST', extra_data=extra)

    def _disposition(self, url):
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        return r['Content-Disposition']

    def test_cs_filename(self, _g):
        self._sub('tok-cs', 'cs')
        self.assertEqual(self._disposition('/forms/tz/tok-cs/pdf/'), 'attachment; filename="Zadani-webu.pdf"')

    def test_en_filename(self, _g):
        self._sub('tok-en', 'en')
        self.assertEqual(self._disposition('/en/forms/tz/tok-en/pdf/'), 'attachment; filename="Website-brief.pdf"')

    def test_lead_lang_wins_over_url(self, _g):
        self._sub('tok-mixed', 'en')
        self.assertEqual(self._disposition('/forms/tz/tok-mixed/pdf/'), 'attachment; filename="Website-brief.pdf"')

    def test_legacy_without_lang_uses_active_language(self, _g):
        self._sub('tok-legacy')
        self.assertEqual(self._disposition('/en/forms/tz/tok-legacy/pdf/'), 'attachment; filename="Website-brief.pdf"')
        self.assertEqual(self._disposition('/forms/tz/tok-legacy/pdf/'), 'attachment; filename="Zadani-webu.pdf"')
