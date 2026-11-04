"""seed_proposal_bukacek — CREATE-ONLY seed of the Bukáček proposal + demo shop.

If the proposal slug already exists, it does nothing and exits 0.
Never deletes, updates or prunes anything. Never prints a password.
"""
import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.proposal_models import Proposal, ProposalModule, ProposalPackage, ProposalSpec
from apps.core.proposal_visual_models import ProposalArchNode, ProposalHighlight

FIXTURE = Path(settings.BASE_DIR) / 'apps' / 'core' / 'fixtures' / 'proposals' / 'bukacek.json'
HOST = 'https://prometeylabs.cz'
TOP = ['client_name', 'kind', 'issued_on', 'is_published', 'title', 'title_en', 'lead', 'lead_en',
       'recommendations_lead', 'recommendations_lead_en', 'cta_label', 'cta_label_en',
       'intro_html', 'intro_html_en', 'guarantee_html', 'guarantee_html_en']


def _cs(row, keys):
    out = dict(row)
    for k in keys:
        if k in row:
            out[k + '_cs'] = row[k]
    return out


class Command(BaseCommand):
    help = 'Create the Bukáček proposal and its demo shop if missing (create-only, never updates or deletes).'

    def handle(self, *args, **options):
        data = json.loads(FIXTURE.read_text(encoding='utf-8'))
        slug = data['slug']
        if Proposal.objects.filter(slug=slug).exists():
            self.stdout.write(f'Proposal {slug} exists, nothing to do.')
            return

        from apps.demoshop.services.provision import provision_demo_shop

        with transaction.atomic():
            fields = _cs({k: data[k] for k in TOP if k in data},
                         ['title', 'lead', 'recommendations_lead', 'cta_label', 'intro_html', 'guarantee_html'])
            p = Proposal.objects.create(slug=slug, **fields)
            for i, r in enumerate(data.get('highlights', [])):
                ProposalHighlight.objects.create(proposal=p, order=i, **_cs(r, ['title']))
            for i, r in enumerate(data.get('arch_nodes', [])):
                ProposalArchNode.objects.create(proposal=p, order=i, **_cs(r, ['title', 'caption']))
            for i, r in enumerate(data.get('modules', [])):
                ProposalModule.objects.create(proposal=p, order=i, number=i + 1, **_cs(r, ['title', 'description']))
            for i, r in enumerate(data.get('packages', [])):
                r = dict(r, price=Decimal(r['price']))
                ProposalPackage.objects.create(proposal=p, order=i, **_cs(r, ['name', 'scope', 'duration']))
            for i, r in enumerate(data.get('specs', [])):
                ProposalSpec.objects.create(proposal=p, order=i, **_cs(r, ['title', 'body']))
            shop = provision_demo_shop(p)

        kp_token = shop.get_kp_token()
        self.stdout.write(f'Created proposal: {HOST}/proposal/{slug}/  (EN: {HOST}/en/proposal/{slug}/)')
        self.stdout.write(f'Demo shop: {HOST}{shop.get_absolute_url()}  login user: {shop.demo_login}')
        self.stdout.write(f'Demo admin entry: {HOST}/demo/{shop.slug}/open/{kp_token}/')
