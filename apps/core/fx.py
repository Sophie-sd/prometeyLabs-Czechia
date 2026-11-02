"""Commercial prices in the visitor's currency. EUR is the base, Kč the local view.

The CZ fork only ever shows EUR and CZK; the rate and the 500 Kč rounding are the
ones the calculator already uses (calculator_estimate.EUR_CZK), so a price quoted
here can never drift away from the price the calculator mails to the lead.
"""
from __future__ import annotations

from decimal import Decimal

from django.utils.translation import get_language

from .calculator_estimate import eur_to_czk_rounded

CURRENCY_COOKIE = 'pl_currency'
CURRENCY_COOKIE_AGE = 60 * 60 * 24 * 365
NBSP = '\u00a0'

SWITCH = (
    ('CZK', 'Kč'),
    ('EUR', '€'),
)
SYMBOLS = dict(SWITCH)
CODES = [code for code, _symbol in SWITCH]


def default_currency(language: str | None = None) -> str:
    """Czech pages open in Kč, the English ones in EUR."""
    lang = (language or get_language() or '').lower()
    return 'EUR' if lang.startswith('en') else 'CZK'


def resolve_currency(request) -> str:
    raw = ''
    if request is not None:
        raw = request.COOKIES.get(CURRENCY_COOKIE, '') or ''
    code = raw.strip().upper()
    return code if code in CODES else default_currency()


def normalize_currency(raw: str | None) -> str:
    code = (raw or '').strip().upper()
    return code if code in CODES else default_currency()


def public_fx(request) -> dict:
    return {'fx_currency': resolve_currency(request), 'fx_codes': CODES}


def _grouped(value: int) -> str:
    return f'{value:,}'.replace(',', NBSP)


def format_eur_number(amount) -> str:
    amount = Decimal(amount)
    if amount == amount.to_integral_value():
        return _grouped(int(amount))
    whole, frac = f'{amount.quantize(Decimal("0.01")):.2f}'.split('.')
    return f'{_grouped(int(whole))}.{frac}'


def convert_amount(amount, currency: str) -> int:
    """EUR → Kč at the calculator rate, rounded to the nearest 500 Kč."""
    return eur_to_czk_rounded(amount) if currency == 'CZK' else int(Decimal(amount))


def format_amount(amount, currency: str) -> str:
    if currency != 'CZK':
        return f'{format_eur_number(amount)}{NBSP}€'
    return f'{_grouped(convert_amount(amount, "CZK"))}{NBSP}Kč'


def format_range(low, high, currency: str) -> str:
    if currency != 'CZK':
        return f'{format_eur_number(low)}–{format_eur_number(high)}{NBSP}€'
    left = convert_amount(low, 'CZK')
    right = convert_amount(high, 'CZK')
    return f'{_grouped(left)}–{_grouped(right)}{NBSP}Kč'


def format_from(amount, currency: str) -> str:
    from django.utils.translation import gettext as _

    return f'{_("od")} {format_amount(amount, currency)}'
