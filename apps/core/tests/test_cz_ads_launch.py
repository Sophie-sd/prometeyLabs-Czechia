"""Pre-Google-Ads launch checks (.cz), on top of test_cz_leads_matrix:

* exact tracking values land in the KeyCRM card comment (utm_source, utm_campaign,
  landing_referrer, landing_page, source_page, form_type, page language);
* EN lead with gclid + cz_eshopy -> source 13, LD_1001, /en/thank-you/;
* the calculator email carries the same "[prometeylabs.cz CZ|EN]" marker as other forms;
* honeypot answer keeps the page language;
* both thank-you pages exist, form JS only follows the server redirect;
* footer services link to an existing block (#services) in CS and EN.

KeyCRM HTTP is always mocked, mail goes to the locmem backend.
"""
import re
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings

from apps.core.models import FormSubmission

from .test_cz_leads_matrix import BASE, _ok, _SyncThread

ROOT = Path(settings.BASE_DIR)


@override_settings(KEYCRM_API_KEY='test-key-not-real', KEYCRM_PIPELINE_ID=6,
                   KEYCRM_GCLID_FIELD_UUID='LD_1001', KEYCRM_SITE_FIELD_UUID='',
                   KEYCRM_LANG_FIELD_UUID='', KEYCRM_NEW_STATUS_ID='',
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   CONTACT_EMAIL='managers@example.test', LEAD_SOURCE_DOMAIN='prometeylabs.cz')
@mock.patch('django.db.close_old_connections', lambda: None)
@mock.patch('apps.core.views.threading.Thread', _SyncThread)
@mock.patch('apps.core.keycrm_service.requests.put')
@mock.patch('apps.core.keycrm_service.requests.post')
class AdsLaunchLeadTests(TestCase):
    TRACKING = {
        'gclid': 'Cj0KCQ-test', 'utm_source': 'google', 'utm_medium': 'cpc',
        'utm_campaign': 'cz_eshopy', 'landing_referrer': 'https://www.google.com/',
        'landing_page': '/internet-shop/?gclid=Cj0KCQ-test', 'source_page': '/internet-shop/',
    }

    def _post(self, url, data):
        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

    def test_card_comment_has_exact_tracking_values_cz(self, post, put):
        post.return_value = _ok()
        body = self._post('/forms/submit/', dict(BASE, form_type='call_request', lang='cs', **self.TRACKING))
        self.assertEqual(body['redirect'], '/thank-you/')
        payload = post.call_args.kwargs['json']
        self.assertEqual(payload['pipeline_id'], 6)
        self.assertEqual(payload['source_id'], 13)
        self.assertIn({'uuid': 'LD_1001', 'value': 'Cj0KCQ-test'}, payload['custom_fields'])
        comment = payload['manager_comment']
        for line in ('utm_source: google', 'utm_campaign: cz_eshopy',
                     'landing_referrer: https://www.google.com/',
                     'landing_page: /internet-shop/?gclid=Cj0KCQ-test',
                     'source_page: /internet-shop/', 'form_type: call-request',
                     'page_language: CZ', 'gclid: Cj0KCQ-test'):
            self.assertIn(line, comment)
        sub = FormSubmission.objects.latest('id')
        self.assertEqual(sub.gclid, 'Cj0KCQ-test')
        self.assertEqual(sub.utm_campaign, 'cz_eshopy')

    def test_en_lead_with_gclid_eshopy(self, post, put):
        post.return_value = _ok()
        body = self._post('/en/forms/submit/', dict(BASE, form_type='contact', message='Hi', lang='en', **self.TRACKING))
        self.assertEqual(body['redirect'], '/en/thank-you/')
        payload = post.call_args.kwargs['json']
        self.assertEqual(payload['source_id'], 13)
        self.assertIn({'uuid': 'LD_1001', 'value': 'Cj0KCQ-test'}, payload['custom_fields'])
        self.assertIn('page_language: EN', payload['manager_comment'])

    def test_en_language_from_referer_when_js_sends_no_lang(self, post, put):
        post.return_value = _ok()
        body = self.client.post('/forms/submit/', dict(BASE, form_type='footer-consultation'),
                                HTTP_REFERER='https://prometeylabs.cz/en/internet-shop/').json()
        self.assertEqual(body['redirect'], '/en/thank-you/')
        self.assertIn('page_language: EN', post.call_args.kwargs['json']['manager_comment'])

    def test_calculator_email_subject_has_site_and_language(self, post, put):
        post.return_value = _ok()
        for prefix, lang, label in (('', 'cs', 'CZ'), ('/en', 'en', 'EN')):
            with self.subTest(lang=lang):
                mail.outbox.clear()
                body = self._post(prefix + '/forms/test/', dict(BASE, lang=lang, question_1='A', gclid='G-1'))
                self.assertEqual(body['redirect'], f'{prefix}/thank-you/')
                self.assertEqual(len(mail.outbox), 1)
                self.assertEqual(mail.outbox[0].to, ['managers@example.test'])
                self.assertTrue(mail.outbox[0].subject.startswith(f'[prometeylabs.cz {label}]'),
                                mail.outbox[0].subject)
                self.assertEqual(post.call_args.kwargs['json']['source_id'], 12)

    def test_honeypot_keeps_page_language(self, post, put):
        body = self.client.post('/forms/submit/', dict(BASE, form_type='telegram-bot', honeypot='bot'),
                                HTTP_REFERER='https://prometeylabs.cz/en/telegram-bot/').json()
        self.assertTrue(body['success'])
        self.assertEqual(body['redirect'], '/en/thank-you/')
        post.assert_not_called()
        self.assertEqual(len(mail.outbox), 0)


class ThankYouAndJsRedirectTests(TestCase):
    def test_thank_you_pages_exist(self):
        for url in ('/thank-you/', '/en/thank-you/'):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_form_js_only_follows_server_redirect(self):
        base = (ROOT / 'static/js/base.js').read_text()
        self.assertIn('window.location.href = data.redirect', base)
        for rel in ('static/js/base.js', 'static/js/home-bundle.js', 'static/js/tz-generator-3.js',
                    'static/js/calculator.js'):
            path = ROOT / rel
            if not path.exists():
                continue
            src = path.read_text()
            # No hardcoded navigation to a thank-you URL.
            self.assertIsNone(re.search(r"location(\.href)?\s*=\s*['\"][^'\"]*thank-you", src), rel)
            self.assertIsNone(re.search(r"location\.(assign|replace)\(\s*['\"][^'\"]*thank-you", src), rel)


class FooterServicesTests(TestCase):
    LABELS = {
        '/': ('Mobilní aplikace', 'Reklama a propagace', 'Správa sociálních sítí'),
        '/en/': ('Mobile app', 'Advertising', 'Social media'),
    }

    def test_footer_service_links_target_existing_block(self):
        for home in ('/', '/en/'):
            html = self.client.get(home).content.decode()
            self.assertIn('id="services"', html, home)
            footer = html[html.index('<footer'):]
            services = footer[:footer.index('plf__col--company')]
            links = re.findall(r'<a href="([^"]+)" class="plf__link">([^<]+)</a>', services)
            by_target = [href for href, _label in links if href.endswith('#services')]
            self.assertEqual(len(by_target), 3, (home, links))
            for href in by_target:
                self.assertEqual(href, f'{home}#services')
        cs_html = self.client.get('/').content.decode()
        for label in self.LABELS['/']:
            self.assertIn(label, cs_html)
