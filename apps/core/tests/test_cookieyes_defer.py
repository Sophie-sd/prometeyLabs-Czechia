from pathlib import Path

from django.template.loader import render_to_string
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]
GTM_HEAD = ROOT / 'templates' / 'partials' / 'gtm_head.html'
BASE_HTML = ROOT / 'templates' / 'base.html'
PROPOSAL_BASE = ROOT / 'templates' / 'proposal' / 'base_proposal.html'
GTM_NOSCRIPT = ROOT / 'templates' / 'partials' / 'gtm_noscript.html'


class CookieYesDeferTests(SimpleTestCase):
    def test_cmp_is_deferred_not_on_window_load(self):
        text = GTM_HEAD.read_text(encoding='utf-8')
        self.assertIn('function _loadCookieYes', text)
        self.assertNotIn("window.addEventListener('load',_loadCookieYes,{once:true})", text)
        self.assertIn('requestIdleCallback', text)
        self.assertIn('timeout:12000', text)
        self.assertIn('setTimeout(_loadCookieYes,12000)', text)
        self.assertIn('_loadCookieYes();', text)
        self.assertNotIn('rel="preconnect" href="https://cdn-cookieyes.com"', text)
        self.assertNotIn(
            'id="cookieyes" type="text/javascript" async',
            text,
        )
        self.assertLess(text.find("gtag('consent','default'"), text.find('function _loadCookieYes'))

    def test_cmp_does_not_bind_scroll_or_mousemove(self):
        text = GTM_HEAD.read_text(encoding='utf-8')
        self.assertIn("['click','touchstart','keydown']", text)
        boot = text.split('window._loadGTM=_loadCookieYes;')[1]
        self.assertNotIn("'scroll'", boot)
        self.assertNotIn("'mousemove'", boot)

    def test_single_gtm_container_mqbjth87(self):
        text = GTM_HEAD.read_text(encoding='utf-8')
        self.assertIn("'dataLayer','GTM-MQBJTH87'", text)
        self.assertNotIn('GTM-K2FVPPTK', text)
        self.assertEqual(text.count("'gtm.start'"), 1)
        # Consent Mode defaults first, then the GTM snippet, then the CMP loader
        self.assertLess(text.find("gtag('consent','default'"), text.find('GTM-MQBJTH87'))
        self.assertLess(text.find('GTM-MQBJTH87'), text.find('function _loadCookieYes'))
        # /thank-you/ still calls window._loadGTM()
        self.assertIn('window._loadGTM=_loadCookieYes;', text)
        noscript = GTM_NOSCRIPT.read_text(encoding='utf-8')
        self.assertIn('ns.html?id=GTM-MQBJTH87', noscript)
        self.assertNotIn('GTM-K2FVPPTK', noscript)

    def test_base_noscript_right_after_body(self):
        text = BASE_HTML.read_text(encoding='utf-8')
        after_body = text.split('<body', 1)[1].split('>', 1)[1].lstrip()
        self.assertTrue(after_body.startswith("{% include 'partials/gtm_noscript.html' %}"))

    def test_public_and_proposal_bases_include_gtm(self):
        for path in (BASE_HTML, PROPOSAL_BASE):
            text = path.read_text(encoding='utf-8')
            self.assertIn("{% include 'partials/gtm_head.html' %}", text)
            self.assertIn("{% include 'partials/gtm_noscript.html' %}", text)


class ProposalGtmCoverageTests(SimpleTestCase):
    def test_proposal_base_renders_gtm_container(self):
        html = render_to_string(
            'proposal/base_proposal.html',
            {
                'LANGUAGE_CODE': 'uk',
                'page_title': 'B2B parts',
                'meta_description': 'Coverage',
                'current_year': 2026,
                'csp_nonce': 'testnonce',
                'COOKIEYES_ID': '',
            },
        )
        self.assertIn('GTM-MQBJTH87', html)
        self.assertNotIn('GTM-K2FVPPTK', html)
        self.assertIn("gtag('consent','default'", html)
        self.assertIn("googletagmanager.com/gtm.js?id='+i+dl", html)
        self.assertIn('googletagmanager.com/ns.html?id=GTM-MQBJTH87', html)
