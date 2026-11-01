"""Ads landing views kept out of views.py (file length)."""
from django.shortcuts import redirect
from django.urls import reverse

from .ads_context import dorobka_ads_context
from .mixins import BasePageView, portfolio_strip


class CanonicalLangSlugMixin:
    """301 the other language's slug to the canonical URL for the active language."""

    canonical_url_name = ''

    def dispatch(self, request, *args, **kwargs):
        canonical = reverse(self.canonical_url_name)
        if request.path != canonical:
            query = request.META.get('QUERY_STRING', '')
            return redirect(f'{canonical}?{query}' if query else canonical, permanent=True)
        return super().dispatch(request, *args, **kwargs)


class DorobkaSajtuView(CanonicalLangSlugMixin, BasePageView):
    template_name = 'pages/dorobka-sajtu.html'
    canonical_url_name = 'dorobka_sajtu'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio_strip'] = portfolio_strip()
        context.update(dorobka_ads_context())
        return context
