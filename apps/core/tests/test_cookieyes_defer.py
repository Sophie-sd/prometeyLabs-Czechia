from pathlib import Path

from django.template.loader import render_to_string
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]
GTM_HEAD = ROOT / 'templates' / 'partials' / 'gtm_head.html'
BASE_HTML = ROOT / 'templates' / 'base.html'
PROPOSAL_BASE = ROOT / 'templates' / 'proposal' / 'base_proposal.html'
GTM_NOSCRIPT = ROOT / 'templates' / 'partials' / 'gtm_noscript.html'


class CookieYesDeferTests(SimpleTestCase):
    """CookieYes тепер вантажиться одразу (без idle/gesture/12 s), Consent default — перед ним."""

    def test_cmp_loads_immediately_after_consent_default(self):
        text = GTM_HEAD.read_text(encoding='utf-8')
        self.assertIn('function _loadCookieYes', text)
        boot = text.split('window._loadGTM=_loadCookieYes;')[1]
        self.assertTrue(boot.lstrip().startswith('_loadCookieYes();'))
        for delayed in ('requestIdleCallback', 'setTimeout(_loadCookieYes', 'timeout:12000',
                        "['click','touchstart','keydown']"):
            self.assertNotIn(delayed, text)
        self.assertIn('s.async=true;', text)
        self.assertNotIn('rel="preconnect" href="https://cdn-cookieyes.com"', text)
        self.assertLess(text.find("gtag('consent','default'"), text.find('function _loadCookieYes'))

    def test_rendered_head_has_cmp_src_with_id(self):
        html = render_to_string('partials/gtm_head.html', {'COOKIEYES_ID': 'testcy', 'csp_nonce': 'n'})
        self.assertIn('cdn-cookieyes.com/client_data/testcy/script.js', html)
        self.assertLess(html.find("gtag('consent','default'"), html.find('cdn-cookieyes.com/client_data'))

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
