"""Pre-Google-Ads перевірка лідів .cz: кожна форма × правило source_id (13/12/14),
pipeline 6, LD_1001, сповіщення менеджерів листом на CONTACT_EMAIL (як на .com),
нормалізація ключа KeyCRM, env_report без секретів (SMTP-перевірка без відправки),
посилання футера.

KeyCRM HTTP завжди замокано; фонова відправка виконується синхронно.
"""
import io
from unittest import mock

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase, override_settings

from apps.core.keycrm_service import KeyCRMService, normalize_api_key

BASE = {'name': 'TEST Jan Novak', 'phone': '+420777123456', 'email': 'test@example.com', 'consent': '1'}

# (url, form_type or None for calculator, extra POST, stored form_type)
FORMS = [
    ('/forms/submit/', 'call_request', {}, 'call-request'),
    ('/forms/submit/', 'footer-consultation', {}, 'footer-consultation'),
    ('/forms/submit/', 'site_request', {'details': 'site_type: eshop'}, 'site-request'),
    ('/forms/submit/', 'contact', {'message': 'TEST message'}, 'contact'),
    ('/forms/submit/', 'telegram-bot', {'bot_task': 'TEST bot'}, 'telegram-bot'),
    ('/forms/test/', None, {'question_1': 'A'}, 'test_result'),
]

# (tracking, expected source_id)
SOURCE_CASES = [
    ({'gclid': 'G-1', 'utm_campaign': 'cz_eshopy'}, 13),
    ({'gclid': 'G-1', 'utm_campaign': 'cz_general'}, 12),
    ({'gclid': 'G-1'}, 12),
    ({'utm_campaign': 'cz_eshopy', 'utm_source': 'google'}, 14),
    ({}, 14),
]


class _SyncThread:
    def __init__(self, target=None, **kw):
        self._target = target

    def start(self):
        self._target()


def _ok(card_id=777):
    r = mock.Mock(status_code=201, text='')
    r.json.return_value = {'id': card_id}
    return r


@override_settings(KEYCRM_API_KEY='test-key-not-real', KEYCRM_PIPELINE_ID=6,
                   KEYCRM_GCLID_FIELD_UUID='LD_1001', KEYCRM_SITE_FIELD_UUID='',
                   KEYCRM_LANG_FIELD_UUID='', KEYCRM_NEW_STATUS_ID='',
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   CONTACT_EMAIL='managers@example.test')
@mock.patch('django.db.close_old_connections', lambda: None)
@mock.patch('apps.core.views.threading.Thread', _SyncThread)
@mock.patch('apps.core.keycrm_service.requests.put')
@mock.patch('apps.core.keycrm_service.requests.post')
class LeadMatrixTests(TestCase):
    def _submit(self, url, form_type, extra, data_extra, prefix='', lang='cs'):
        data = dict(BASE, lang=lang, source_page='/x/', landing_page='/internet-shop/',
                    landing_referrer='https://www.google.com/', **extra, **data_extra)
        if form_type:
            data['form_type'] = form_type
        r = self.client.post(prefix + url, data)
        self.assertEqual(r.status_code, 200, r.content)
        body = r.json()
        self.assertTrue(body['success'], body)
        return body

    def test_every_form_source_id_matrix(self, post, put):
        post.return_value = _ok()
        for url, form_type, extra, stored in FORMS:
            for tracking, expected in SOURCE_CASES:
                with self.subTest(form=stored, tracking=tracking):
                    post.reset_mock()
                    self._submit(url, form_type, extra, tracking)
                    self.assertEqual(post.call_count, 1)
                    self.assertTrue(post.call_args.args[0].endswith('/pipelines/cards'))
                    payload = post.call_args.kwargs['json']
                    self.assertEqual(payload['pipeline_id'], 6)
                    self.assertEqual(payload['source_id'], expected)
                    self.assertNotIn('status_id', payload)  # перший статус воронки = «Новий»
                    if tracking.get('gclid'):
                        self.assertIn({'uuid': 'LD_1001', 'value': 'G-1'}, payload['custom_fields'])
                    else:
                        self.assertNotIn('custom_fields', payload)
                    c = payload['manager_comment']
                    for line in (f'form_type: {stored}', 'page_language: CZ',
                                 'landing_referrer: https://www.google.com/',
                                 'landing_page: /internet-shop/'):
                        self.assertIn(line, c)
                    self.assertIn('utm_source: ', c)
                    self.assertIn('utm_campaign: ', c)
                    self.assertRegex(c, r'source_page: \S+')

    def test_managers_notified_by_email_cz_and_en(self, post, put):
        post.return_value = _ok()
        for url, form_type, extra, stored in FORMS:
            for prefix, lang, label, thanks in (('', 'cs', 'CZ', '/thank-you/'),
                                                ('/en', 'en', 'EN', '/en/thank-you/')):
                with self.subTest(form=stored, lang=lang):
                    mail.outbox.clear()
                    post.reset_mock()
                    body = self._submit(url, form_type, extra, {'gclid': 'G-1'}, prefix=prefix, lang=lang)
                    self.assertEqual(body['redirect'], thanks)
                    self.assertEqual(len(mail.outbox), 1)
                    self.assertEqual(mail.outbox[0].to, ['managers@example.test'])
                    self.assertIn('TEST Jan Novak', mail.outbox[0].body)
                    self.assertEqual(post.call_count, 1)
                    self.assertIn(f'page_language: {label}', post.call_args.kwargs['json']['manager_comment'])

    def test_keycrm_failure_does_not_break_response_or_email(self, post, put):
        post.return_value = mock.Mock(status_code=401, text='{"message":"Unauthenticated."}')
        mail.outbox.clear()
        body = self._submit('/forms/submit/', 'contact', {'message': 'x'}, {})
        self.assertEqual(body['redirect'], '/thank-you/')
        self.assertEqual(len(mail.outbox), 1)


class ApiKeyNormalizationTests(SimpleTestCase):
    def test_normalize(self):
        for raw in ('abc123', ' abc123\n', '"abc123"', "'abc123'", 'Bearer abc123', ' bearer  abc123 '):
            self.assertEqual(normalize_api_key(raw), 'abc123', raw)
        self.assertEqual(normalize_api_key(''), '')
        self.assertEqual(normalize_api_key(None), '')

    @override_settings(KEYCRM_API_KEY=' Bearer abc123\n')
    def test_header_uses_normalized_key(self):
        self.assertEqual(KeyCRMService()._headers['Authorization'], 'Bearer abc123')


class EnvReportSmtpCheckTests(SimpleTestCase):
    SECRET = 'super-secret-app-password'

    def _run(self, smtp_cls):
        out = io.StringIO()
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
                               EMAIL_HOST='smtp.gmail.com', EMAIL_PORT=587, EMAIL_USE_TLS=True,
                               EMAIL_HOST_USER='user@example.test', EMAIL_HOST_PASSWORD=self.SECRET,
                               KEYCRM_API_KEY=' Bearer ' + self.SECRET), \
                mock.patch('smtplib.SMTP', smtp_cls), \
                mock.patch('apps.core.keycrm_service.requests.get') as get:
            get.return_value = mock.Mock(status_code=401, text='{"message":"Unauthenticated."}')
            call_command('env_report', stdout=out)
        text = out.getvalue()
        self.assertNotIn(self.SECRET, text)
        self.assertNotIn('user@example.test', text)
        return text

    def test_login_ok_no_mail_sent(self):
        smtp = mock.MagicMock()
        text = self._run(smtp)
        self.assertIn('SMTP check OK', text)
        conn = smtp.return_value
        conn.starttls.assert_called_once()
        conn.login.assert_called_once()
        conn.sendmail.assert_not_called()
        conn.send_message.assert_not_called()
        self.assertIn('bearer_prefix=yes', text)
        self.assertIn('surrounding_whitespace=yes', text)

    def test_disconnect_reported_with_stage(self):
        import smtplib
        smtp = mock.MagicMock()
        smtp.return_value.login.side_effect = smtplib.SMTPServerDisconnected('Connection unexpectedly closed')
        text = self._run(smtp)
        self.assertIn('SMTP check FAILED at login: SMTPServerDisconnected', text)


class FooterLinksTests(TestCase):
    def test_service_links_point_to_home_services(self):
        for url, home in (('/contacts/', '/'), ('/en/contacts/', '/en/')):
            html = self.client.get(url).content.decode()
            footer = html[html.index('<footer'):]
            services = footer[:footer.index('plf__col--company')]
            self.assertEqual(services.count(f'href="{home}#services"'), 3, url)
            self.assertNotIn('/calculator/', services, url)
            self.assertNotIn(f'href="{home}portfolio/" class="plf__link">Mobil', services)
