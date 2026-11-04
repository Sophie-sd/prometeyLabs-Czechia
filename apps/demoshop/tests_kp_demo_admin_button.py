"""KP -> demo admin button: fresh signed link per request, cs/en, scoping, tampered/expired rejected."""
import datetime
import re
from urllib.parse import unquote
from unittest import mock

from django.core import signing
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.proposal_models import Proposal
from apps.demoshop.catalog_models import ShopProduct
from apps.demoshop.services.provision import provision_demo_shop

LINK_RE = re.compile(r'href="(/demo/[^/"]+/open/[^/"]+/\?lang=(cs|en))"')


def _proposal(name, with_shop=True):
    p = Proposal.objects.create(slug=f'kp-{name.lower()}', title=name, client_name=name,
                                is_published=True, issued_on=datetime.date(2026, 11, 4))
    shop = provision_demo_shop(p) if with_shop else None
    return p, shop


class KpDemoAdminButtonTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.p, cls.shop = _proposal('Bukacek')
        cls.p2, cls.other = _proposal('Jiny')
        cls.p3, _ = _proposal('Bezdema', with_shop=False)

    def _kp_url(self, lang):
        with translation.override(lang):
            return reverse('proposal_detail', kwargs={'slug': self.p.slug})

    def _link(self, lang):
        r = self.client.get(self._kp_url(lang))
        self.assertEqual(r.status_code, 200)
        m = LINK_RE.search(r.content.decode())
        self.assertIsNotNone(m, 'demo admin button missing')
        self.assertEqual(m.group(2), lang)
        return r, m.group(1).replace('&amp;', '&')

    def test_button_cs_and_en_text_and_valid_link(self):
        for lang, text in (('cs', 'Vstoupit do administrace dema'), ('en', 'Open demo admin')):
            with self.subTest(lang=lang):
                r, link = self._link(lang)
                self.assertContains(r, text)
                self.assertIn(f'/demo/{self.shop.slug}/open/', link)
                token = link.split('/open/')[1].split('/')[0]
                signing.TimestampSigner(salt='demo-admin-login.v1:kp').unsign(unquote(token), max_age=60)

    def test_no_button_without_demo_shop(self):
        with translation.override('cs'):
            r = self.client.get(reverse('proposal_detail', kwargs={'slug': self.p3.slug}))
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(LINK_RE.search(r.content.decode()))

    def test_follow_cs_lands_on_demo_admin_cs_scoped(self):
        _, link = self._link('cs')
        r = self.client.get(link, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.redirect_chain[-1][0], '/demo-admin/')
        self.assertContains(r, 'lang="cs"')
        r = self.client.get(reverse('demo_admin:demoshop_shopproduct_changelist'))
        self.assertEqual(r.status_code, 200)
        own = ShopProduct.objects.filter(shop=self.shop).first()
        foreign = ShopProduct.objects.filter(shop=self.other).first()
        if own and foreign:
            self.assertEqual(self.client.get(reverse('demo_admin:demoshop_shopproduct_change',
                                                     args=[foreign.pk])).status_code in (302, 404), True)
            self.assertEqual(self.client.get(reverse('demo_admin:demoshop_shopproduct_change',
                                                     args=[own.pk])).status_code, 200)

    def test_follow_en_lands_on_demo_admin_en(self):
        _, link = self._link('en')
        r = self.client.get(link, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'lang="en"')

    def test_tampered_token_rejected(self):
        _, link = self._link('cs')
        prefix, rest = link.split('/open/')
        token = rest.split('/')[0]
        bad = token[:-2] + ('AA' if token[-2:] != 'AA' else 'BB')
        r = self.client.get(f'{prefix}/open/{bad}/?lang=cs')
        self.assertEqual(r.status_code, 404)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_token_for_other_shop_rejected(self):
        _, link = self._link('cs')
        token = link.split('/open/')[1].split('/')[0]
        r = self.client.get(f'/demo/{self.other.slug}/open/{token}/')
        self.assertEqual(r.status_code, 404)

    def test_expired_token_rejected(self):
        _, link = self._link('cs')
        real_time = signing.time.time
        with mock.patch('django.core.signing.time.time', return_value=real_time() + 91 * 86400):
            r = self.client.get(link)
        self.assertEqual(r.status_code, 404)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_token_is_fresh_per_request_not_stored(self):
        from apps.demoshop.models import DemoShop
        _, link = self._link('cs')
        token = link.split('/open/')[1].split('/')[0]
        for f in DemoShop._meta.concrete_fields:
            self.assertNotEqual(str(getattr(self.shop, f.attname)), unquote(token))
