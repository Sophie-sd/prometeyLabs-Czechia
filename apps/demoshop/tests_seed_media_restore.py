"""Render has no persistent disk: media vanish on deploy. reseed must restore missing seed files."""
import datetime
import shutil
import tempfile

from django.test import TestCase, override_settings

from apps.core.proposal_models import Proposal
from apps.demoshop.models import ShopBlock
from apps.demoshop.services.provision import provision_demo_shop
from apps.demoshop.services.seed import seed_demo_shop

TMP = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TMP)
class SeedRestoresMissingMediaTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP, ignore_errors=True)

    def test_missing_files_are_restored(self):
        p = Proposal.objects.create(slug='kp-media', title='M', client_name='M', is_published=True,
                                    issued_on=datetime.date(2026, 11, 4))
        shop = provision_demo_shop(p)
        shutil.rmtree(TMP, ignore_errors=True)
        seed_demo_shop(shop)
        prod = shop.products.first() if hasattr(shop, 'products') else None
        for img in (prod.images.all() if prod else []):
            self.assertTrue(img.image.storage.exists(img.image.name), img.image.name)
        for slide in shop.hero_slides.all() if hasattr(shop, 'hero_slides') else []:
            self.assertTrue(slide.image.storage.exists(slide.image.name))
        for b in ShopBlock.objects.filter(shop=shop).exclude(value_image=''):
            self.assertTrue(b.value_image.storage.exists(b.value_image.name))
