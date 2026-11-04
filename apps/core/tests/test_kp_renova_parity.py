"""Renova parity for the KP page: tenant-aware demo CTA + '#prop-demo' section with demo admin entry."""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.proposal_models import Proposal
from apps.demoshop.services.provision import provision_demo_shop


def _kp(slug, **kw):
    return Proposal.objects.create(slug=slug, title=slug, client_name=slug, is_published=True,
                                   issued_on=datetime.date(2026, 11, 4), **kw)


class KpRenovaParityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.shop_kp = _kp('kp-parity-shop')
        cls.shop = provision_demo_shop(cls.shop_kp)
        cls.bare_kp = _kp('kp-parity-bare')

    def _get(self, kp, lang):
        with translation.override(lang):
            url = reverse('proposal_detail', kwargs={'slug': kp.slug})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        return r

    def test_demo_section_cs(self):
        r = self._get(self.shop_kp, 'cs')
        self.assertContains(r, 'id="prop-demo"')
        self.assertContains(r, 'Demo je připravené')
        self.assertContains(r, 'Zobrazit demo obchodu')
        self.assertContains(r, 'data-qa="kp-demo-admin-section"')
        self.assertContains(r, self.shop.get_absolute_url())
        self.assertContains(r, 'data-prop-section="10"')

    def test_demo_section_en(self):
        r = self._get(self.shop_kp, 'en')
        self.assertContains(r, 'The demo is ready')
        self.assertContains(r, 'View shop demo')
        self.assertContains(r, 'Open demo admin')

    def test_no_demo_section_without_tenant(self):
        r = self._get(self.bare_kp, 'cs')
        self.assertNotContains(r, 'id="prop-demo"')
        self.assertNotContains(r, 'data-qa="kp-demo-admin')
        self.assertContains(r, 'id="prop-cta" class="prop-section prop-section--alt prop-cta-sec" data-prop-section="09"')

    def test_cta_label_follows_tenant_type(self):
        kp = Proposal.objects.get(pk=self.shop_kp.pk)
        kp.kind = Proposal.DemoKind.LANDING  # tenant is a shop -> shop label wins (Renova)
        with translation.override('en'):
            self.assertEqual(str(kp.demo_cta_label), 'View shop demo')
        with translation.override('en'):
            self.assertEqual(str(self.bare_kp.demo_cta_label), {
                Proposal.DemoKind.SHOP: 'View shop demo',
                Proposal.DemoKind.LANDING: 'View landing demo',
                Proposal.DemoKind.CORPORATE: 'View website demo',
            }.get(self.bare_kp.kind, 'View demo'))
