"""P1-3/P1-4 (QA 2026-11-04), adapted onto Oleg's DemoAdminSite + signed-token login:
demo admin in Czech (cs default), scoped to own shop, staff /admin/ stays uk."""
import datetime
import json

from django.core.signing import TimestampSigner
from django.test import TestCase
from django.urls import reverse

from apps.core.proposal_models import Proposal
from apps.demoshop.catalog_models import ShopCategory, ShopProduct
from apps.demoshop.demo_auth_views import DEMO_LOGIN_SALT
from apps.demoshop.services.provision import provision_demo_shop


def _shop(name):
    p = Proposal.objects.create(slug=f'kp-{name}', title=name, client_name=name, is_published=True,
                                issued_on=datetime.date(2026, 11, 4))
    return provision_demo_shop(p)


def _kp_link(shop):
    token = TimestampSigner(salt=f'{DEMO_LOGIN_SALT}:kp').sign(json.dumps({'demo_id': shop.pk}))
    return f'/demo/{shop.slug}/open/{token}/'


class DemoAdminCzechLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.shop = _shop('Alfa')
        cls.other = _shop('Beta')
        cls.user = cls.shop.owner_user
        cls.cat = ShopCategory.objects.filter(shop=cls.shop).first()
        cls.prod = ShopProduct.objects.filter(shop=cls.shop).first()
        cls.other_prod = ShopProduct.objects.filter(shop=cls.other).first()
        cls.other_cat = ShopCategory.objects.filter(shop=cls.other).first()

    def _login(self):
        r = self.client.get(_kp_link(self.shop))
        self.assertEqual(r.status_code, 302)

    def test_demo_user_is_not_superuser(self):
        self.assertFalse(self.user.is_superuser)

    def test_get_admin_login_is_gone(self):
        r = self.client.get(reverse('demoshop:admin_login', kwargs={'shop_slug': self.shop.slug}))
        self.assertEqual(r.status_code, 404)

    def test_demo_admin_renders_cs(self):
        self._login()
        page = self.client.get('/demo-admin/')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'lang="cs"')

    def test_staff_admin_stays_uk(self):
        page = self.client.get(reverse('admin:login'))
        self.assertContains(page, 'lang="uk"')

    def test_changelists_and_change_views_ok(self):
        self._login()
        urls = [
            reverse('demo_admin:demoshop_shopproduct_changelist'),
            reverse('demo_admin:demoshop_shopcategory_changelist'),
            reverse('demo_admin:demoshop_shopblock_changelist'),
        ]
        if self.prod:
            urls.append(reverse('demo_admin:demoshop_shopproduct_change', args=[self.prod.pk]))
        if self.cat:
            urls.append(reverse('demo_admin:demoshop_shopcategory_change', args=[self.cat.pk]))
        for url in urls:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200)
                self.assertContains(r, 'lang="cs"')

    def test_other_demo_objects_invisible(self):
        if not (self.prod and self.other_prod):
            self.skipTest('provision created no products')
        self._login()
        r = self.client.get(reverse('demo_admin:demoshop_shopproduct_changelist'))
        self.assertNotContains(r, reverse('demo_admin:demoshop_shopproduct_change', args=[self.other_prod.pk]))
        r = self.client.get(reverse('demo_admin:demoshop_shopproduct_change', args=[self.other_prod.pk]))
        self.assertIn(r.status_code, (302, 404))

    def test_admin_access_page_does_not_leak_password(self):
        r = self.client.get(reverse('demoshop:admin_access', kwargs={'shop_slug': self.shop.slug}))
        self.assertEqual(r.status_code, 404)

    def test_order_admin_hides_np_technical_fields(self):
        self._login()
        from apps.demoshop.order_models import ShopOrder
        o = ShopOrder.objects.create(shop=self.shop, customer_name='T', phone='1', email='a@b.cz', total=1)
        r = self.client.get(reverse('demo_admin:demoshop_shoporder_change', args=[o.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'np_city_ref')
        self.assertNotContains(r, 'np_city_name_ru')
