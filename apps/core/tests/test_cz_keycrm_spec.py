"""ТЗ CZ Leads: pipeline 6, LD_1001, source_id 12/13/14, сирий трекінг у коментарі,
редирект на /thank-you/ | /en/thank-you/ для КОЖНОЇ форми, WhatsApp-текст.

KeyCRM HTTP завжди замокано (requests.post / requests.put), фонова відправка теж.
"""
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.test import TestCase, SimpleTestCase, override_settings
from django.utils import translation

from apps.core.keycrm_service import resolve_keycrm_source_id, sync_submission_to_keycrm
from apps.core.models import FormSubmission

ROOT = Path(settings.BASE_DIR)

TRACKING = {
    'gclid': 'TEST-GCLID-1',
    'utm_source': 'google',
    'utm_medium': 'cpc',
    'utm_campaign': 'cz_eshopy',
    'landing_page': '/internet-shop/',
    'landing_referrer': 'https://www.google.com/',
    'source_page': '/contacts/',
}

BASE = {'name': 'TEST Jan Novak', 'phone': '+420777123456', 'email': 'test@example.com', 'consent': '1'}

# (form_type for /forms/submit/, extra POST fields)
SUBMIT_FORMS = [
    ('call_request', {}),
    ('footer-consultation', {}),
    ('contact', {'message': 'TEST message from contact form'}),
    ('site_request', {'details': 'site_type: eshop'}),
    ('telegram-bot', {'bot_task': 'TEST bot task', 'message': 'TEST tg message'}),
    ('consultation', {'topic': 'TEST topic'}),
]


def _ok(card_id=501):
    r = mock.Mock(status_code=201, text='')
    r.json.return_value = {'id': card_id}
    return r


def _sub(**kw):
    return SimpleNamespace(gclid=kw.get('gclid', ''), utm_campaign=kw.get('utm_campaign', ''))


class SourceIdRulesTests(SimpleTestCase):
    def test_gclid_eshopy_is_13(self):
        self.assertEqual(resolve_keycrm_source_id(_sub(gclid='g', utm_campaign='cz_eshopy')), 13)
        self.assertEqual(resolve_keycrm_source_id(_sub(gclid='g', utm_campaign=' CZ_Eshopy ')), 13)

    def test_gclid_general_or_empty_or_unknown_is_12(self):
        for camp in ('cz_general', '', 'something_else', 'cz_eshopy_v2'):
            self.assertEqual(resolve_keycrm_source_id(_sub(gclid='g', utm_campaign=camp)), 12, camp)

    def test_no_gclid_is_14_even_with_campaign(self):
        for camp in ('', 'cz_eshopy', 'cz_general'):
            self.assertEqual(resolve_keycrm_source_id(_sub(utm_campaign=camp)), 14, camp)

    def test_never_15(self):
        for g in ('', 'g'):
            for camp in ('', 'cz_eshopy', 'cz_general', 'x'):
                self.assertNotEqual(resolve_keycrm_source_id(_sub(gclid=g, utm_campaign=camp)), 15)

    @override_settings(KEYCRM_SOURCE_CZ_ORGANIC=15)
    def test_15_blocked_even_if_misconfigured(self):
        self.assertIsNone(resolve_keycrm_source_id(_sub()))

    def test_settings_defaults(self):
        self.assertEqual(settings.KEYCRM_PIPELINE_ID, 6)
        self.assertEqual(settings.KEYCRM_GCLID_FIELD_UUID, 'LD_1001')
        self.assertEqual((settings.KEYCRM_SOURCE_CZ_ESHOPY, settings.KEYCRM_SOURCE_CZ_GENERAL,
                          settings.KEYCRM_SOURCE_CZ_ORGANIC), (13, 12, 14))


@override_settings(KEYCRM_API_KEY='test-key-not-real', KEYCRM_PIPELINE_ID=6,
                   KEYCRM_GCLID_FIELD_UUID='LD_1001', KEYCRM_SITE_FIELD_UUID='',
                   KEYCRM_LANG_FIELD_UUID='', KEYCRM_NEW_STATUS_ID='')
@mock.patch('apps.core.keycrm_service.requests.put')
@mock.patch('apps.core.keycrm_service.requests.post')
@mock.patch('apps.core.tz_views._dispatch_async')
@mock.patch('apps.core.views._dispatch_async')
class EveryFormEndToEndTests(TestCase):
    """POST кожної форми CZ+EN → redirect + payload KeyCRM."""

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def _payload_for_last(self, post):
        post.reset_mock()
        post.return_value = _ok()
        sub = FormSubmission.objects.latest('id')
        sync_submission_to_keycrm(sub)
        self.assertEqual(post.call_count, 1)
        self.assertTrue(post.call_args.args[0].endswith('/pipelines/cards'))
        return sub, post.call_args.kwargs['json']

    def _assert_payload(self, payload, form_key, lang_label, expect_message=None, source=13):
        self.assertEqual(payload['pipeline_id'], 6)
        self.assertEqual(payload['source_id'], source)
        self.assertNotIn('status_id', payload)
        self.assertEqual(payload['contact']['full_name'], 'TEST Jan Novak')
        self.assertEqual(payload['contact']['phone'], '+420777123456')
        self.assertEqual(payload['contact']['email'], 'test@example.com')
        self.assertIn({'uuid': 'LD_1001', 'value': 'TEST-GCLID-1'}, payload['custom_fields'])
        c = payload['manager_comment']
        for line in (
            f'form_type: {form_key}', f'page_language: {lang_label}', 'utm_source: google',
            'utm_campaign: cz_eshopy', 'landing_referrer: https://www.google.com/',
            'landing_page: /internet-shop/', 'gclid: TEST-GCLID-1', 'Source: prometeylabs.cz',
        ):
            self.assertIn(line, c)
        self.assertRegex(c, r'source_page: \S+')
        if expect_message:
            self.assertIn(expect_message, c)

    def _post(self, url, data):
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200, r.content)
        body = r.json()
        self.assertTrue(body['success'], body)
        return body

    def test_submit_forms_cz_and_en(self, d, tzd, post, put):
        stored_key = {'call_request': 'call-request', 'site_request': 'site-request'}
        for form_type, extra in SUBMIT_FORMS:
            for prefix, lang, label, thanks in (('', 'cs', 'CZ', '/thank-you/'),
                                                ('/en', 'en', 'EN', '/en/thank-you/')):
                with self.subTest(form=form_type, lang=lang):
                    data = dict(BASE, form_type=form_type, lang=lang, **TRACKING, **extra)
                    body = self._post(f'{prefix}/forms/submit/', data)
                    self.assertEqual(body['redirect'], thanks)
                    sub, payload = self._payload_for_last(post)
                    self._assert_payload(payload, stored_key.get(form_type, form_type), label,
                                         expect_message=extra.get('message') or extra.get('topic'))

    def test_lang_from_url_prefix_without_post_lang(self, d, tzd, post, put):
        body = self._post('/en/forms/submit/', dict(BASE, form_type='contact', **TRACKING))
        self.assertEqual(body['redirect'], '/en/thank-you/')
        body = self._post('/forms/submit/', dict(BASE, form_type='contact', **TRACKING))
        self.assertEqual(body['redirect'], '/thank-you/')

    def test_calculator_cz_and_en(self, d, tzd, post, put):
        for prefix, lang, label, thanks in (('', 'cs', 'CZ', '/thank-you/'), ('/en', 'en', 'EN', '/en/thank-you/')):
            with self.subTest(lang=lang):
                body = self._post(f'{prefix}/forms/test/',
                                  dict(BASE, lang=lang, question_1='A', **TRACKING))
                self.assertEqual(body['redirect'], thanks)
                _sub, payload = self._payload_for_last(post)
                self._assert_payload(payload, 'test_result', label)

    def test_tz_generator_cz_and_en_redirect_with_pdf_token(self, d, tzd, post, put):
        quiz = json.dumps({'site_type': 'landing', 'description': 'TEST tz description'})
        for prefix, lang, label, thanks in (('', 'cs', 'CZ', '/thank-you/'), ('/en', 'en', 'EN', '/en/thank-you/')):
            with self.subTest(lang=lang):
                body = self._post(f'{prefix}/forms/tz/', dict(BASE, lang=lang, quiz=quiz, **TRACKING))
                self.assertTrue(body['redirect'].startswith(thanks + '?tz='), body['redirect'])
                token = body['token']
                self.assertEqual(body['redirect'], f'{thanks}?tz={token}')
                _sub, payload = self._payload_for_last(post)
                self._assert_payload(payload, 'tz_generator', label, expect_message='TEST tz description')
                self.assertIn('source_page: /contacts/', payload['manager_comment'])
                page = self.client.get(body['redirect'])
                self.assertEqual(page.status_code, 200)
                html = page.content.decode()
                self.assertIn(f'/forms/tz/{token}/pdf/', html)
                self.assertIn(f'/forms/tz/{token}/upsell/', html)
                self.assertIn('noindex', html)
                pdf = self.client.get(f'/forms/tz/{token}/pdf/')
                self.assertEqual(pdf.status_code, 200)
                self.assertEqual(pdf['Content-Type'], 'application/pdf')

    def test_thank_you_ignores_unknown_tz_token(self, d, tzd, post, put):
        html = self.client.get('/thank-you/?tz=does-not-exist').content.decode()
        self.assertNotIn('data-tz-thanks', html)

    def test_source_12_and_14(self, d, tzd, post, put):
        self._post('/forms/submit/', dict(BASE, form_type='contact', **dict(TRACKING, utm_campaign='cz_general')))
        _s, p = self._payload_for_last(post)
        self.assertEqual(p['source_id'], 12)
        no_gclid = {k: v for k, v in TRACKING.items() if k != 'gclid'}
        self._post('/forms/submit/', dict(BASE, form_type='contact', **no_gclid))
        _s, p = self._payload_for_last(post)
        self.assertEqual(p['source_id'], 14)
        self.assertNotIn('custom_fields', p)
        self.assertIn('gclid: -', p['manager_comment'])

    @override_settings(KEYCRM_NEW_STATUS_ID='321')
    def test_new_status_put_when_configured(self, d, tzd, post, put):
        put.return_value = mock.Mock(status_code=200, text='')
        self._post('/forms/submit/', dict(BASE, form_type='contact', **TRACKING))
        self._payload_for_last(post)
        put.assert_called_once()
        self.assertTrue(put.call_args.args[0].endswith('/pipelines/cards/501'))
        self.assertEqual(put.call_args.kwargs['json'], {'status_id': 321})

    def test_no_status_put_by_default(self, d, tzd, post, put):
        self._post('/forms/submit/', dict(BASE, form_type='contact', **TRACKING))
        self._payload_for_last(post)
        put.assert_not_called()


class TemplatesSendTrackingTests(SimpleTestCase):
    def test_all_submitters_use_gclid_capture(self):
        for js in ('static/js/base.js', 'static/js/home-bundle.js', 'static/js/tz-generator-3.js'):
            self.assertIn('GCLIDCapture.appendToFormData', (ROOT / js).read_text(encoding='utf-8'), js)

    def test_gclid_capture_sends_lang_and_source_page(self):
        js = (ROOT / 'static/js/core/gclid-capture.js').read_text(encoding='utf-8')
        self.assertIn("setField(formData, 'lang'", js)
        self.assertIn("setField(formData, 'source_page'", js)
        for key in ('gclid', 'utm_source', 'utm_campaign', 'landing_referrer', 'landing_path'):
            self.assertIn(key, js)

    def test_tz_js_redirects(self):
        js = (ROOT / 'static/js/tz-generator-3.js').read_text(encoding='utf-8')
        self.assertIn('window.location.href = data.redirect', js)


NODE = shutil.which('node')
_HARNESS = r"""
const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8');
const [lang,search,path]=[process.argv[2],process.argv[3],process.argv[4]];
const listeners=[];const store={};
global.window={location:{search,pathname:path,host:'prometeylabs.cz',protocol:'https:',href:'https://prometeylabs.cz'+path,origin:'https://prometeylabs.cz'},
  sessionStorage:{getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=v},removeItem:k=>{delete store[k]}}};
global.location=window.location;
global.document={documentElement:{getAttribute:()=>lang},cookie:'',referrer:'',readyState:'complete',addEventListener:(t,f)=>listeners.push([t,f])};
eval(src);
let href='https://wa.me/420777000000';
const a={href,textContent:'WA',dataset:{},getAttribute:k=>k==='href'?href:null,setAttribute:(k,v)=>{href=v;a.href=v}};
listeners.filter(l=>l[0]==='click').forEach(l=>l[1]({target:{closest:()=>a}}));
console.log(new URL(href).searchParams.get('text')||'');
"""


class WhatsAppPrefillTests(SimpleTestCase):
    def _text(self, lang, search, path='/'):
        if not NODE:
            self.skipTest('node not installed')
        out = subprocess.run([NODE, '-e', _HARNESS, str(ROOT / 'static/js/core/gclid-capture.js'), lang, search, path],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout.strip()

    def test_gclid_without_tag_generic_cs(self):
        self.assertEqual(self._text('cs', '?gclid=abc&utm_campaign=cz_general'), 'Poptávka z Google Ads')

    def test_gclid_without_tag_generic_en(self):
        self.assertEqual(self._text('en', '?gclid=abc', '/en/'), 'Google Ads enquiry')

    def test_tagged_text_kept(self):
        self.assertEqual(self._text('cs', '?gclid=abc&utm_campaign=cz_eshopy'), 'Poptávka z Google Ads: E-shopy')
        self.assertEqual(self._text('en', '?gclid=abc&utm_campaign=corp', '/en/'), 'Google Ads enquiry: Corporate websites')

    def test_no_gclid_on_campaign_pages_no_text(self):
        # Organic visitors on the campaign landing pages must not get the Google Ads prefill.
        self.assertEqual(self._text('cs', '', '/internet-shop/'), '')
        self.assertEqual(self._text('cs', '', '/corporate-website/'), '')
        self.assertEqual(self._text('en', '?utm_campaign=cz_eshopy', '/en/internet-shop/'), '')
        self.assertEqual(self._text('cs', '?utm_campaign=corp', '/corporate-website/'), '')

    def test_gclid_capture_include_version(self):
        for tpl in ('templates/base.html', 'templates/pages/home.html',
                    'templates/pages/thank_you.html', 'templates/pages/internet-shop-v2.html'):
            src = (ROOT / tpl).read_text(encoding='utf-8')
            self.assertIn("gclid-capture.js' %}?v=6", src, tpl)
            self.assertNotIn("gclid-capture.js' %}?v=5", src, tpl)

    def test_no_gclid_no_tag_no_text(self):
        self.assertEqual(self._text('cs', ''), '')


class EnvReportNoSecretsTests(SimpleTestCase):
    def test_secret_values_never_printed(self):
        import io
        import os
        from django.core.management import call_command
        env = {'KEYCRM_API_KEY': '', 'EMAIL_HOST_PASSWORD': 'TOPSECRET-VALUE-123',
               'EMAIL_HOST_USER': 'secret-user@example.com'}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env), override_settings(KEYCRM_API_KEY=''):
            call_command('env_report', stdout=buf)
        out = buf.getvalue()
        self.assertIn('EMAIL_HOST_PASSWORD=yes', out)
        self.assertIn('EMAIL_HOST_USER=yes', out)
        self.assertNotIn('TOPSECRET-VALUE-123', out)
        self.assertNotIn('secret-user@example.com', out)
        self.assertIn('KEYCRM_PIPELINE_ID=6', out)
