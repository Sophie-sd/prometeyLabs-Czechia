from django import template
from django.utils.translation import gettext as _

from apps.core.fx import SWITCH, default_currency, format_amount, format_from, format_range

register = template.Library()

_VARIANTS = {'light', 'dark'}
_REGIONS = {'home', 'shop', 'soft'}
_NAMES = {'CZK': 'Koruna', 'EUR': 'Euro'}


def _cur(context):
    return context.get('fx_currency') or default_currency()


@register.simple_tag(takes_context=True)
def fx_amount(context, amount):
    return format_amount(amount, _cur(context))


@register.simple_tag(takes_context=True)
def fx_range(context, low, high):
    return format_range(low, high, _cur(context))


@register.simple_tag(takes_context=True)
def fx_from(context, amount):
    return format_from(amount, _cur(context))


@register.inclusion_tag('components/currency_switcher.html', takes_context=True)
def currency_switcher(context, variant='light', region='home', slot=''):
    if variant not in _VARIANTS:
        variant = 'light'
    if region not in _REGIONS:
        region = 'home'
    request = context.get('request')
    current = _cur(context)
    choices = [
        {'code': code, 'symbol': symbol, 'name': _(_NAMES[code]), 'current': code == current}
        for code, symbol in SWITCH
    ]
    return {
        'choices': choices,
        'next': request.get_full_path() if request is not None else '/',
        'variant': variant,
        # slot: a second switcher of the same region on one page needs its own DOM id
        'dom_id': f'{region}-{slot}' if slot else region,
        'csrf_token': context.get('csrf_token'),
    }
