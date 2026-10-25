import json
import re

from django.test import Client, SimpleTestCase, TestCase

from apps.core.consent_models import ConsentLog


def _head(html):
    return html.split('</head>', 1)[0]


class ConsentDefaultBeforeTagsTests(TestCase):
    """Consent Mode v2 default (denied) must run before any Google tag, CZ + EN."""

    def _get(self, url):
        r = Client().get(url)
        self.assertEqual(r.status_code, 200, url)
        return r.content.decode('utf-8')

    def test_default_denied_before_gtm_on_cs_and_en(self):
        for url in ('/', '/en/', '/web-development/', '/en/web-development/'):
            html = self._get(url)
            head = _head(html)
            i_default = head.find("gtag('consent','default'")
            self.assertNotEqual(i_default, -1, url)
            block = head[i_default:head.find('});', i_default)]
            for key in ('ad_storage', 'ad_user_data', 'ad_personalization', 'analytics_storage'):
                self.assertRegex(block, rf"{key}:'denied'", f'{url} {key}')
            self.assertIn("functionality_storage:'granted'", block)
            self.assertIn("security_storage:'granted'", block)
            # no Google tag / CMP script tag anywhere before the default
            for marker in ('googletagmanager.com/gtag/js', 'googletagmanager.com/gtm.js', 'cdn-cookieyes.com'):
                idx = html.find(marker)
                self.assertTrue(idx == -1 or idx > i_default, f'{url} {marker}')
            self.assertNotIn('<script async src="https://www.googletagmanager.com', html)
            self.assertNotIn('ns.html?id=GTM', html)  # no noscript tag without consent
            self.assertNotIn('preconnect" href="https://www.googletagmanager.com', head)

    def test_gtm_only_loaded_through_consent_gate(self):
        html = self._get('/')
        head = _head(html)
        self.assertIn('if(o&&(o.a||o.m))loadGTM();', head)
        self.assertEqual(head.count('gtm.js?id='), 1)

    def test_banner_cs_and_en_equal_buttons_and_links(self):
        cs = self._get('/web-development/')
        for s in ('Přijmout vše', 'Odmítnout vše', 'Nastavení', 'href="/cookies/"', 'id="pl-consent"'):
            self.assertIn(s, cs)
        en = self._get('/en/web-development/')
        for s in ('Accept all', 'Reject all', 'Settings', 'href="/en/cookies/"'):
            self.assertIn(s, en)
        # Accept and Reject share exactly the same class (equal prominence)
        rej = re.search(r'class="([^"]+)" data-plc-act="reject_all"', cs).group(1)
        acc = re.search(r'class="([^"]+)" data-plc-act="accept_all"', cs).group(1)
        self.assertEqual(rej, acc)
        # nothing pre-ticked except the disabled "necessary" box
        boxes = re.findall(r'<input[^>]*data-plc="[am]"[^>]*>', cs)
        self.assertEqual(len(boxes), 2)
        for box in boxes:
            self.assertNotIn('checked', box)
        self.assertIn('data-cookie-settings', cs)  # footer re-open / withdraw link

    def test_banner_hidden_server_side_when_choice_stored(self):
        c = Client()
        c.cookies['pl_consent'] = '{"v":1,"a":0,"m":0}'
        html = c.get('/').content.decode('utf-8')
        self.assertRegex(html, r'id="pl-consent"[^>]* hidden>')


class ConsentLogEndpointTests(TestCase):
    def test_logs_valid_choice(self):
        r = Client().post('/consent/log/', data=json.dumps(
            {'id': 'a' * 32, 'action': 'reject_all', 'a': 0, 'm': 0, 'lang': 'cs', 'path': '/'}),
            content_type='application/json')
        self.assertEqual(r.status_code, 200)
        row = ConsentLog.objects.get()
        self.assertEqual(row.action, 'reject_all')
        self.assertFalse(row.analytics or row.marketing)

    def test_rejects_garbage(self):
        c = Client()
        self.assertEqual(c.post('/consent/log/', data='x', content_type='application/json').status_code, 400)
        self.assertEqual(c.post('/consent/log/', data=json.dumps({'id': 'zz', 'action': 'accept_all'}),
                                content_type='application/json').status_code, 400)
        self.assertEqual(c.get('/consent/log/').status_code, 405)
        self.assertEqual(ConsentLog.objects.count(), 0)
