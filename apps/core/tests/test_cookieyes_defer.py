"""GTM / consent wiring (formerly CookieYes loader tests).

CookieYes was replaced by the first-party banner (partials/consent_banner.html);
GTM-MQBJTH87 now loads only after consent (Consent Mode v2 basic mode).
"""
from pathlib import Path

from django.template.loader import render_to_string
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]
GTM_HEAD = ROOT / 'templates' / 'partials' / 'gtm_head.html'
BASE_HTML = ROOT / 'templates' / 'base.html'
PROPOSAL_BASE = ROOT / 'templates' / 'proposal' / 'base_proposal.html'
GTM_NOSCRIPT = ROOT / 'templates' / 'partials' / 'gtm_noscript.html'


class GtmWiringTests(SimpleTestCase):
    def test_no_cookieyes_script_loaded(self):
        html = render_to_string('partials/gtm_head.html', {'COOKIEYES_ID': 'testcy', 'csp_nonce': 'n'})
        self.assertNotIn('cdn-cookieyes.com', html)

    def test_single_gtm_container_mqbjth87(self):
        text = GTM_HEAD.read_text(encoding='utf-8')
        self.assertIn("GTM='GTM-MQBJTH87'", text)
        self.assertNotIn('GTM-K2FVPPTK', text)
        self.assertEqual(text.count("'gtm.start'"), 1)
        self.assertLess(text.find("gtag('consent','default'"), text.find('gtm.js?id='))
        # /thank-you/ still calls window._loadGTM()
        self.assertIn('w._loadGTM=function', text)

    def test_noscript_has_no_tag_before_consent(self):
        self.assertNotIn('<iframe', GTM_NOSCRIPT.read_text(encoding='utf-8'))

    def test_base_noscript_right_after_body(self):
        text = BASE_HTML.read_text(encoding='utf-8')
        after_body = text.split('<body', 1)[1].split('>', 1)[1].lstrip()
        self.assertTrue(after_body.startswith("{% include 'partials/gtm_noscript.html' %}"))

    def test_public_and_proposal_bases_include_gtm_and_banner(self):
        for path in (BASE_HTML, PROPOSAL_BASE):
            text = path.read_text(encoding='utf-8')
            self.assertIn("{% include 'partials/gtm_head.html' %}", text)
            self.assertIn("{% include 'partials/consent_banner.html' %}", text)


class ProposalGtmCoverageTests(SimpleTestCase):
    def test_proposal_base_renders_consent_and_gtm_loader(self):
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
        self.assertIn("googletagmanager.com/gtm.js?id='+GTM", html)
        self.assertIn('id="pl-consent"', html)
