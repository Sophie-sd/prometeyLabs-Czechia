"""contact_click, /thank-you/ redirect, KeyCRM source/lang tags, manager e-mail, ensure_admin."""
import os
from pathlib import Path
from unittest import mock

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import translation

from apps.core.form_handlers import page_language_label, send_form_email
from apps.core.keycrm_service import sync_submission_to_keycrm
from apps.core.models import FormSubmission

ROOT = Path(settings.BASE_DIR)


def _lead(**extra):
    data = {
        'name': 'TEST Jan Novak',
        'email': 'test@example.com',
        'consent': '1',
        'phone': '+420777123456',
        'form_type': 'contact',
        'message': 'TEST lead',
        'gclid': 'TESTGCLID',
        'utm_source': 'google',
        'utm_campaign': 'cz_corp',
        'landing_page': '/corporate-website/',
    }
    data.update(extra)
    return data


class ContactClickSnippetTests(TestCase):
    def test_js_pushes_contact_click_for_three_channels(self):
        js = (ROOT / 'static/js/core/gclid-capture.js').read_text(encoding='utf-8')
        self.assertIn("event: 'contact_click'", js)
        for channel in ("'whatsapp'", "'telegram'", "'email'"):
            self.assertIn(channel, js)
        self.assertIn("mailto:", js)
        self.assertIn('trackContactClicks();', js)

    def test_script_loaded_on_pages(self):
        for url in ('/', '/contacts/', '/en/', '/internet-shop/', '/thank-you/', '/en/thank-you/'):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertIn('js/core/gclid-capture.js', r.content.decode(), url)
        translation.activate(settings.LANGUAGE_CODE)


class ThankYouPagesTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_cs_and_en_pages_noindex(self):
        for url in ('/thank-you/', '/en/thank-you/'):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertIn('noindex', r.content.decode())

    @mock.patch('apps.core.views._dispatch_async')
    def test_redirect_by_page_language(self, _d):
        r = self.client.post('/forms/submit/', _lead(), HTTP_REFERER='http://testserver/contacts/')
        self.assertEqual(r.json()['redirect'], '/thank-you/')
        r = self.client.post('/forms/submit/', _lead(form_type='footer-consultation'),
                             HTTP_REFERER='http://testserver/en/')
        self.assertEqual(r.json()['redirect'], '/en/thank-you/')
        sub = FormSubmission.objects.latest('id')
        self.assertEqual(sub.gclid, 'TESTGCLID')
        self.assertEqual(sub.extra_data['landing_page'], '/corporate-website/')


class KeyCRMNonBlockingTests(TestCase):
    def _submission(self, lang_referer='http://testserver/contacts/'):
        with mock.patch('apps.core.views._dispatch_async'):
            r = self.client.post('/forms/submit/', _lead(), HTTP_REFERER=lang_referer)
        self.assertTrue(r.json()['success'])
        return FormSubmission.objects.latest('id')

    @override_settings(KEYCRM_API_KEY='')
    def test_without_key_nothing_sent(self):
        sub = self._submission()
        with mock.patch('apps.core.keycrm_service.requests.post') as post:
            sync_submission_to_keycrm(sub)
        post.assert_not_called()

    @override_settings(KEYCRM_API_KEY='test-key')
    def test_keycrm_down_does_not_raise_and_lead_kept(self):
        sub = self._submission()
        with mock.patch('apps.core.keycrm_service.requests.post',
                        side_effect=requests.ConnectionError('down')):
            sync_submission_to_keycrm(sub)
        sub.refresh_from_db()
        self.assertFalse(sub.keycrm_synced)

    @override_settings(KEYCRM_API_KEY='test-key')
    def test_payload_has_source_lang_form_gclid_utm(self):
        sub = self._submission(lang_referer='http://testserver/en/contacts/')
        resp = mock.Mock(status_code=201)
        resp.json.return_value = {'id': 77}
        with mock.patch('apps.core.keycrm_service.requests.post', return_value=resp) as post:
            sync_submission_to_keycrm(sub)
        payload = post.call_args.kwargs['json']
        comment = payload['manager_comment']
        self.assertIn('Source: prometeylabs.cz', comment)
        self.assertIn('Page language: EN', comment)
        self.assertIn('Form: contact', comment)
        self.assertIn('GCLID: TESTGCLID', comment)
        self.assertIn('/corporate-website/', comment)
        self.assertEqual(payload['utm_source'], 'google')
        self.assertEqual(payload['utm_campaign'], 'cz_corp')
        sub.refresh_from_db()
        self.assertEqual(sub.keycrm_card_id, 77)


class ManagerEmailTests(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                       CONTACT_EMAIL='manager@example.com')
    def test_email_subject_and_body_have_source_and_language(self):
        ok, _err = send_form_email({
            'type': 'Contact', 'name': 'TEST', 'phone': '+420777123456', 'timestamp': 'now',
            'lead_source': 'prometeylabs.cz', 'page_language': 'CZ', 'lang': 'cs',
        })
        self.assertTrue(ok)
        self.assertEqual(mail.outbox[0].to, ['manager@example.com'])
        self.assertIn('prometeylabs.cz CZ', mail.outbox[0].subject)
        self.assertIn('Source: prometeylabs.cz', mail.outbox[0].body)

    def test_page_language_label(self):
        self.assertEqual(page_language_label('cs'), 'CZ')
        self.assertEqual(page_language_label('en'), 'EN')
        self.assertEqual(page_language_label(''), '')


class EnsureAdminTests(TestCase):
    def _run(self, **env):
        keys = ('ENSURE_ADMIN_USERNAME', 'ENSURE_ADMIN_EMAIL',
                'ENSURE_ADMIN_PASSWORD_HASH', 'ENSURE_ADMIN_PASSWORD')
        clean = {k: v for k, v in os.environ.items() if k not in keys}
        clean.update(env)
        with mock.patch.dict(os.environ, clean, clear=True):
            call_command('ensure_admin', stdout=open(os.devnull, 'w'))

    def test_skip_without_env(self):
        self._run()
        self.assertFalse(get_user_model().objects.exists())

    def test_creates_superuser_from_hash(self):
        self._run(ENSURE_ADMIN_USERNAME='admin-test', ENSURE_ADMIN_PASSWORD_HASH=make_password('s3cret-TEST-pw'))
        u = get_user_model().objects.get(username='admin-test')
        self.assertTrue(u.is_staff and u.is_superuser and u.is_active)
        self.assertTrue(u.check_password('s3cret-TEST-pw'))

    def test_existing_user_untouched(self):
        User = get_user_model()
        u = User.objects.create_user('admin-test', password='old-pw', is_staff=False)
        self._run(ENSURE_ADMIN_USERNAME='admin-test', ENSURE_ADMIN_PASSWORD='new-pw')
        u.refresh_from_db()
        self.assertTrue(u.check_password('old-pw'))
        self.assertFalse(u.is_superuser)

    def test_invalid_hash_skipped(self):
        self._run(ENSURE_ADMIN_USERNAME='admin-test', ENSURE_ADMIN_PASSWORD_HASH='not-a-hash')
        self.assertFalse(get_user_model().objects.filter(username='admin-test').exists())
