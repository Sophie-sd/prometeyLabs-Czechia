from django import template
from django.urls import reverse
from django.utils.translation import get_language

from apps.core.calc_cta import CALC_START_QUERY, calc_cta_copy

register = template.Library()


def _ctx(context, page, part, position='hero'):
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
        'position': position,
        'sticky_desktop': data['sticky_desktop'],
        'sticky_arrow': data['sticky_arrow'],
        'sticky_event': data['sticky_event'],
        'csp_nonce': context.get('csp_nonce', ''),
    }


@register.inclusion_tag('components/calc_cta/hero.html', takes_context=True)
def calc_cta(context, page, part='block', position='hero'):
    """Calc CTA. part: 'block' (hero button + micro), 'btn' or 'micro' (for flex rows),
    'wide' (secondary centred button lower on the page; position = data-calc-cta, e.g. 'why')."""
    return _ctx(context, page, part, position)


@register.inclusion_tag('components/calc_cta/sticky.html', takes_context=True)
def calc_cta_sticky(context, page):
    """Sticky bar (mobile ≤767px; + desktop if the page config says so) + CSS/JS loader; render once per page."""
    return _ctx(context, page, 'sticky')
