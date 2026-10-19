"""Price guide for the /web-development/ page (cs default, /en/).

Ranges and timelines mirror the homepage canon (components/home/redesign_why.html,
"average price ranges" + "timelines"). EUR is the primary currency; CZK is shown
only as an orientation at the calculator rate (calculator_estimate.EUR_CZK).
"""
from __future__ import annotations

from django.utils.translation import get_language

from .calculator_estimate import eur_to_czk_rounded

NBSP = '\u00a0'

# key -> (EUR low, EUR high)
WEB_DEV_TIERS = (
    ('landing', 400, 700),
    ('corporate', 700, 1000),
    ('shop', 1400, 2800),
    ('app', 2800, 8000),
)


def _group(value: int, lang: str) -> str:
    if lang == 'en':
        return f'{value:,}'
    return f'{value:,}'.replace(',', NBSP)


def _czk(eur: int) -> int:
    return eur_to_czk_rounded(eur)


def format_eur_range(low: int, high: int, lang: str) -> str:
    if lang == 'en':
        return f'€{_group(low, lang)}–{_group(high, lang)}'
    return f'{_group(low, lang)}–{_group(high, lang)}{NBSP}€'


def format_czk_range(low: int, high: int, lang: str) -> str:
    lo, hi = _czk(low), _czk(high)
    if lang == 'en':
        return f'≈{NBSP}CZK{NBSP}{_group(lo, lang)}–{_group(hi, lang)}'
    return f'≈{NBSP}{_group(lo, lang)}–{_group(hi, lang)}{NBSP}Kč'


def format_eur_amount(value: int, lang: str) -> str:
    if lang == 'en':
        return f'€{_group(value, lang)}'
    return f'{_group(value, lang)}{NBSP}€'


def format_czk_amount(value: int, lang: str) -> str:
    czk = _czk(value)
    if lang == 'en':
        return f'≈{NBSP}CZK{NBSP}{_group(czk, lang)}'
    return f'≈{NBSP}{_group(czk, lang)}{NBSP}Kč'


def web_dev_prices(lang: str | None = None) -> dict:
    """{key: {low, high, eur, czk, eur_from, czk_from}} for the active language."""
    lang = (lang or get_language() or 'cs').split('-')[0].lower()
    lang = 'en' if lang == 'en' else 'cs'
    prices = {}
    for key, low, high in WEB_DEV_TIERS:
        prices[key] = {
            'low': low,
            'high': high,
            'eur': format_eur_range(low, high, lang),
            'czk': format_czk_range(low, high, lang),
            'eur_from': format_eur_amount(low, lang),
            'czk_from': format_czk_amount(low, lang),
        }
    return prices
