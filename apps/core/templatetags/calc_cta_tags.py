from django import template
from django.urls import reverse
from django.utils.translation import get_language

from apps.core.calc_cta import CALC_START_QUERY, calc_cta_copy

register = template.Library()


def _ctx(context, page, part):
    data = calc_cta_copy(page, get_language())
    target = data['target']
    if target.startswith('#'):
        href, scroll_target = target, target
    else:
        href, scroll_target = reverse('calculator') + CALC_START_QUERY, ''
    return {
        'page': page,
        'part': part,
        'label': data['sticky'] if part == 'sticky' else data['label'],
        'micro': data['micro'],
        'href': href,
        'scroll_target': scroll_target,
        'csp_nonce': context.get('csp_nonce', ''),
    }


@register.inclusion_tag('components/calc_cta/hero.html', takes_context=True)
def calc_cta(context, page, part='block'):
    """Hero CTA. part: 'block' (button + micro), 'btn' or 'micro' (for flex rows)."""
    return _ctx(context, page, part)


@register.inclusion_tag('components/calc_cta/sticky.html', takes_context=True)
def calc_cta_sticky(context, page):
    """Mobile sticky bar (≤767px) + CSS/JS loader; render once per page."""
    return _ctx(context, page, 'sticky')
