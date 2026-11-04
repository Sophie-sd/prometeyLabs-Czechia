"""Views для standalone-сторінок комерційних пропозицій."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView

from apps.core.proposal_models import Proposal, ProposalSpec
from apps.core.utils import get_site_contact_settings


class ProposalDetailView(DetailView):
    """Публічна сторінка КП за slug (лише is_published=True)."""

    model = Proposal
    template_name = 'proposal/detail.html'
    context_object_name = 'proposal'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return (
            Proposal.objects.filter(is_published=True)
            .select_related('demo_shop')
            .prefetch_related('modules', 'packages', 'specs', 'highlights', 'arch_nodes')
        )

    def get_object(self, queryset=None):
        qs = queryset if queryset is not None else self.get_queryset()
        return get_object_or_404(qs, slug=self.kwargs.get(self.slug_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.object
        specs = list(proposal.specs.all())
        arch_nodes = list(proposal.arch_nodes.all())
        title = proposal.get_localized_title()
        lead = proposal.get_localized_lead()
        context.update({
            'page_title': title,
            'meta_description': (lead or title)[:160],
            'og_title': title,
            'keywords': '',
            'current_year': timezone.now().year,
            'contacts': get_site_contact_settings(),
            'modules': proposal.modules.all(),
            'packages': proposal.packages.all(),
            'highlights': list(proposal.highlights.all()),
            'arch_root': arch_nodes[0] if arch_nodes else None,
            'arch_branches': arch_nodes[1:] if arch_nodes else [],
            'spec_items': [s for s in specs if s.kind == ProposalSpec.Kind.SPEC],
            'payment_items': [s for s in specs if s.kind == ProposalSpec.Kind.PAYMENT],
            'recommendation_items': [
                s for s in specs if s.kind == ProposalSpec.Kind.RECOMMENDATION
            ],
            'kp_demo_admin_url': self._demo_admin_url(proposal),
        })
        return context

    def _demo_admin_url(self, proposal):
        """Fresh signed KP link per request (never stored/logged); None without an active DemoShop."""
        from django.urls import reverse
        from django.utils.translation import get_language
        try:
            shop = proposal.demo_shop
        except Exception:
            return None
        if not shop or not shop.is_active:
            return None
        lang = (get_language() or 'cs')[:2]
        lang = lang if lang in ('cs', 'en') else 'cs'
        url = reverse('demo_open_link', kwargs={'shop_slug': shop.slug, 'kp_token': shop.get_kp_token()})
        return f'{url}?lang={lang}'
