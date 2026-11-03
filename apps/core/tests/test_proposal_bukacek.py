"""seed_proposal_bukacek: create-only, never touches an existing proposal."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.core.proposal_models import Proposal
from apps.demoshop.models import DemoShop

SLUG = 'bukacek-katalog-recenzi-7k2m'


class SeedProposalBukacekTests(TestCase):
    def run_cmd(self):
        out = StringIO()
        call_command('seed_proposal_bukacek', stdout=out)
        return out.getvalue()

    def test_creates_proposal_and_shop(self):
        out = self.run_cmd()
        p = Proposal.objects.get(slug=SLUG)
        self.assertEqual(p.kind, 'shop')
        self.assertEqual(p.packages.count(), 2)
        self.assertEqual(p.packages.order_by('order').first().duration_en, '3 weeks')
        shop = DemoShop.objects.get(proposal=p)
        self.assertTrue(shop.slug.isascii())
        self.assertIn('https://prometeylabs.cz/proposal/', out)
        self.assertNotIn('prometey-labs.com', out)
        self.assertNotIn(shop.demo_password, out)
        self.assertNotIn('password', out.lower())

    def test_second_run_is_noop(self):
        self.run_cmd()
        p = Proposal.objects.get(slug=SLUG)
        p.title = 'Edited in admin'; p.save()
        counts = (p.specs.count(), p.packages.count(), DemoShop.objects.count())
        out = self.run_cmd()
        p.refresh_from_db()
        self.assertEqual(p.title, 'Edited in admin')
        self.assertEqual(counts, (p.specs.count(), p.packages.count(), DemoShop.objects.count()))
        self.assertIn('nothing to do', out)

    def test_existing_proposal_without_shop_gets_no_shop(self):
        Proposal.objects.create(slug=SLUG, client_name='x', kind='shop', issued_on='2026-11-03')
        self.run_cmd()
        self.assertFalse(DemoShop.objects.exists())
