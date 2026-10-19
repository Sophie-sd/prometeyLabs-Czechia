"""
П.12: кожен лід у KeyCRM має site=cz і lang=cs|en.

KeyCRM HTTP завжди замокано (requests.post), реальних запитів немає.
Фонова відправка (_dispatch_async) теж замокана, щоб тести не запускали потоки.
"""
import json
from unittest import mock

from django.test import TestCase, override_settings

from apps.core.keycrm_service import (
    KeyCRMService,
    lead_site_and_lang,
    sync_submission_to_keycrm,
)
from apps.core.models import FormSubmission


def _lead(**extra):
    data = {
        'name': 'TEST Jan Novak',
        'email': 'test@example.com',
        'consent': '1',
        'phone': '+420777123456',
        'form_type': 'contact',
        'message': 'TEST lead',
    }
    data.update(extra)
    return data


@mock.patch('apps.core.tz_views._dispatch_async')
@mock.patch('apps.core.views._dispatch_async')
class LeadSiteLangCaptureTests(TestCase):
    """site/lang записуються в FormSubmission.extra_data для всіх ендпоінтів."""

    def tearDown(self):
        from django.conf import settings as dj_settings
        from django.utils import translation
        translation.activate(dj_settings.LANGUAGE_CODE)

    def _last(self):
        return FormSubmission.objects.latest('id')

    def test_cz_page_unprefixed_endpoint_is_cs(self, _d, _tz):
        r = self.client.post(
            '/forms/submit/', _lead(),
            HTTP_REFERER='http://testserver/contacts/',
        )
        self.assertEqual(r.status_code, 200, r.content)
        sub = self._last()
        self.assertEqual(sub.extra_data['site'], 'cz')
        self.assertEqual(sub.extra_data['lang'], 'cs')

    def test_en_prefixed_endpoint_is_en(self, _d, _tz):
        r = self.client.post('/en/forms/submit/', _lead())
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self._last().extra_data['lang'], 'en')
        self.assertEqual(self._last().extra_data['site'], 'cz')

    def test_unprefixed_endpoint_from_en_page_uses_referer(self, _d, _tz):
        # home-bundle.js шле на /forms/submit/ навіть з /en/
        r = self.client.post(
            '/forms/submit/', _lead(form_type='footer-consultation'),
            HTTP_REFERER='http://testserver/en/',
        )
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self._last().extra_data['lang'], 'en')

    def test_explicit_post_lang_wins(self, _d, _tz):
        self.client.post('/forms/submit/', _lead(lang='en'))
        self.assertEqual(self._last().extra_data['lang'], 'en')

    def test_unsupported_post_lang_ignored(self, _d, _tz):
        self.client.post('/forms/submit/', _lead(lang='uk'))
        self.assertEqual(self._last().extra_data['lang'], 'cs')

    def test_no_referer_defaults_to_cs(self, _d, _tz):
        self.client.post('/forms/submit/', _lead())
        self.assertEqual(self._last().extra_data['lang'], 'cs')

    def test_quiz_site_request_keeps_gclid_and_tags(self, _d, _tz):
        r = self.client.post(
            '/en/forms/submit/',
            _lead(form_type='site_request', details='TEST quiz', gclid='TEST-GCLID-1',
                  source_page='/en/internet-shop-v2/'),
        )
        self.assertEqual(r.status_code, 200, r.content)
        sub = self._last()
        self.assertEqual(sub.gclid, 'TEST-GCLID-1')
        self.assertEqual(sub.extra_data['source_page'], '/en/internet-shop-v2/')
        self.assertEqual((sub.extra_data['site'], sub.extra_data['lang']), ('cz', 'en'))

    def test_calculator_endpoint(self, _d, _tz):
        r = self.client.post('/en/forms/test/', {
            'name': 'TEST Jan', 'phone': '+420777123456', 'consent': '1',
            'question_1': 'A',
        })
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(json.loads(r.content)['success'])
        sub = self._last()
        self.assertEqual(sub.form_type, 'test_result')
        self.assertEqual((sub.extra_data['site'], sub.extra_data['lang']), ('cz', 'en'))

    def test_tz_generator_endpoint(self, _d, _tz):
        r = self.client.post('/forms/tz/', {
            'name': 'TEST Jan', 'phone': '+420777123456', 'email': 'test@example.com',
            'quiz': json.dumps({'description': 'TEST'}),
            'consent': '1',
        })
        self.assertEqual(r.status_code, 200, r.content)
        sub = self._last()
        self.assertEqual(sub.form_type, 'tz_generator')
        self.assertEqual((sub.extra_data['site'], sub.extra_data['lang']), ('cz', 'cs'))

    def test_telegram_bot_endpoint(self, _d, _tz):
        r = self.client.post(
            '/en/forms/submit/', _lead(form_type='telegram-bot', bot_task='TEST'),
        )
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self._last().extra_data['lang'], 'en')


def _ok_response(card_id=777):
    resp = mock.Mock()
    resp.status_code = 201
    resp.json.return_value = {'id': card_id}
    resp.text = ''
    return resp


@override_settings(
    KEYCRM_API_KEY='test-key-not-real',
    KEYCRM_GCLID_FIELD_UUID='',
    KEYCRM_SITE_FIELD_UUID='',
    KEYCRM_LANG_FIELD_UUID='',
)
@mock.patch('apps.core.keycrm_service.requests.post')
class KeyCRMPayloadSiteLangTests(TestCase):
    """Payload у KeyCRM (requests.post замокано)."""

    def _sub(self, **kw):
        data = dict(
            form_type='contact', name='TEST Jan', phone='+420777123456',
            email='test@example.com',
            extra_data={'site': 'cz', 'lang': 'en', 'source_page': '/en/contacts/'},
        )
        data.update(kw)
        return FormSubmission.objects.create(**data)

    def _payload(self, post_mock):
        self.assertEqual(post_mock.call_count, 1)
        args, kwargs = post_mock.call_args
        self.assertTrue(args[0].endswith('/pipelines/cards'))
        return kwargs['json']

    def test_manager_comment_has_site_and_lang(self, post_mock):
        post_mock.return_value = _ok_response()
        ok, card_id, err = KeyCRMService().create_pipeline_card(self._sub())
        self.assertTrue(ok)
        self.assertEqual(card_id, 777)
        comment = self._payload(post_mock)['manager_comment']
        self.assertIn('Site: cz', comment)
        self.assertIn('Lang: en', comment)

    def test_no_custom_fields_without_uuids(self, post_mock):
        post_mock.return_value = _ok_response()
        KeyCRMService().create_pipeline_card(self._sub())
        self.assertNotIn('custom_fields', self._payload(post_mock))

    @override_settings(KEYCRM_SITE_FIELD_UUID='uuid-site', KEYCRM_LANG_FIELD_UUID='uuid-lang',
                       KEYCRM_GCLID_FIELD_UUID='uuid-gclid')
    def test_custom_fields_when_uuids_configured(self, post_mock):
        post_mock.return_value = _ok_response()
        KeyCRMService().create_pipeline_card(self._sub(gclid='TEST-GCLID'))
        fields = {f['uuid']: f['value'] for f in self._payload(post_mock)['custom_fields']}
        self.assertEqual(fields, {
            'uuid-gclid': 'TEST-GCLID', 'uuid-site': 'cz', 'uuid-lang': 'en',
        })

    @override_settings(KEYCRM_GCLID_FIELD_UUID='uuid-gclid')
    def test_gclid_custom_field_unchanged(self, post_mock):
        post_mock.return_value = _ok_response()
        KeyCRMService().create_pipeline_card(self._sub(gclid='TEST-GCLID'))
        payload = self._payload(post_mock)
        self.assertEqual(payload['custom_fields'], [{'uuid': 'uuid-gclid', 'value': 'TEST-GCLID'}])
        self.assertIn('GCLID: TEST-GCLID', payload['manager_comment'])

    def test_legacy_submission_without_tags_gets_site(self, post_mock):
        post_mock.return_value = _ok_response()
        sub = self._sub(extra_data=None, preferred_language='cs')
        self.assertEqual(lead_site_and_lang(sub), ('cz', 'cs'))
        KeyCRMService().create_pipeline_card(sub)
        comment = self._payload(post_mock)['manager_comment']
        self.assertIn('Site: cz', comment)
        self.assertIn('Lang: cs', comment)

    def test_sync_marks_submission(self, post_mock):
        post_mock.return_value = _ok_response(card_id=4242)
        sub = self._sub()
        sync_submission_to_keycrm(sub)
        sub.refresh_from_db()
        self.assertTrue(sub.keycrm_synced)
        self.assertEqual(sub.keycrm_card_id, 4242)

    @override_settings(KEYCRM_API_KEY='')
    def test_unconfigured_key_sends_nothing(self, post_mock):
        sync_submission_to_keycrm(self._sub())
        post_mock.assert_not_called()


@mock.patch('apps.core.keycrm_service.requests.post')
@mock.patch('apps.core.views._dispatch_async')
class EndToEndViewToPayloadTests(TestCase):
    """Форма → FormSubmission → payload KeyCRM (без мережі)."""

    @override_settings(KEYCRM_API_KEY='test-key-not-real', KEYCRM_GCLID_FIELD_UUID='')
    def test_en_contact_form_payload(self, dispatch_mock, post_mock):
        post_mock.return_value = _ok_response()
        r = self.client.post('/en/forms/submit/', _lead(gclid='TEST-GCLID-E2E'))
        self.assertEqual(r.status_code, 200, r.content)
        dispatch_mock.assert_called_once()
        sub = FormSubmission.objects.get(id=dispatch_mock.call_args[0][0])
        sync_submission_to_keycrm(sub)
        payload = post_mock.call_args.kwargs['json']
        self.assertIn('Site: cz', payload['manager_comment'])
        self.assertIn('Lang: en', payload['manager_comment'])
        self.assertIn('GCLID: TEST-GCLID-E2E', payload['manager_comment'])
        self.assertEqual(payload['contact']['phone'], '+420777123456')
