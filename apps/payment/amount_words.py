"""Amount in words for invoices: Czech and English, EUR and USD.

num2words is not installed in this project, so the conversion is implemented
here (supports 0 … 999 999 999 999).
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

# ── English ──────────────────────────────────────────────────────────────
_EN_ONES = [
    'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
    'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
    'seventeen', 'eighteen', 'nineteen',
]
_EN_TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
_EN_SCALES = [(10 ** 9, 'billion'), (10 ** 6, 'million'), (1000, 'thousand')]


def _en_below_1000(n: int) -> str:
    parts = []
    if n >= 100:
        parts.append(f'{_EN_ONES[n // 100]} hundred')
        n %= 100
    if n >= 20:
        tens = _EN_TENS[n // 10]
        parts.append(f'{tens}-{_EN_ONES[n % 10]}' if n % 10 else tens)
    elif n:
        parts.append(_EN_ONES[n])
    return ' '.join(parts)


def int_to_words_en(n: int) -> str:
    if n == 0:
        return 'zero'
    parts = []
    for value, word in _EN_SCALES:
        if n >= value:
            parts.append(f'{_en_below_1000(n // value)} {word}')
            n %= value
    if n:
        parts.append(_en_below_1000(n))
    return ' '.join(parts)


# ── Czech ────────────────────────────────────────────────────────────────
_CS_ONES = ['', 'jeden', 'dva', 'tři', 'čtyři', 'pět', 'šest', 'sedm', 'osm', 'devět']
_CS_TEENS = [
    'deset', 'jedenáct', 'dvanáct', 'třináct', 'čtrnáct', 'patnáct',
    'šestnáct', 'sedmnáct', 'osmnáct', 'devatenáct',
]
_CS_TENS = ['', '', 'dvacet', 'třicet', 'čtyřicet', 'padesát', 'šedesát', 'sedmdesát', 'osmdesát', 'devadesát']
_CS_HUNDREDS = ['', 'sto', 'dvě stě', 'tři sta', 'čtyři sta', 'pět set', 'šest set', 'sedm set', 'osm set', 'devět set']

# gender: 'm' (dolar, cent, tisíc, milion), 'n' (euro), 'f' (miliarda)
_CS_ONE = {'m': 'jeden', 'f': 'jedna', 'n': 'jedno'}
_CS_TWO = {'m': 'dva', 'f': 'dvě', 'n': 'dvě'}


def _cs_below_1000(n: int, gender: str, compound: bool = False) -> str:
    """Words for 1..999. Gender only affects a standalone final 1/2.

    Compound numbers ending in 1 use the invariant «jedna» (dvacet jedna,
    tisíc jedna) + genitive plural of the noun — the standard form in Czech
    amounts (dvacet jedna eur, sto jedna dolarů).
    """
    parts = []
    h, rest = divmod(n, 100)
    if h:
        parts.append(_CS_HUNDREDS[h])
    if 10 <= rest <= 19:
        parts.append(_CS_TEENS[rest - 10])
    else:
        t, o = divmod(rest, 10)
        if t:
            parts.append(_CS_TENS[t])
        if o == 1:
            parts.append('jedna' if (parts or compound) else _CS_ONE[gender])
        elif o == 2:
            parts.append(_CS_TWO[gender])
        elif o:
            parts.append(_CS_ONES[o])
    return ' '.join(parts)


def cs_noun_form(n: int, one: str, few: str, many: str) -> str:
    """Czech noun agreement with the final element of the numeral.

    1 → nominative singular; 2–4 (and compounds ending in 2–4, e.g. 22, 103)
    → nominative plural; everything else incl. 0, 5–20, 21, 25, 100 → genitive plural.
    """
    if n == 1:
        return one
    last_two = n % 100
    last = n % 10
    if 2 <= last <= 4 and not (12 <= last_two <= 14):
        return few
    return many


def int_to_words_cs(n: int, gender: str = 'm') -> str:
    if n == 0:
        return 'nula'
    parts = []
    scales = [
        (10 ** 9, 'f', ('miliarda', 'miliardy', 'miliard')),
        (10 ** 6, 'm', ('milion', 'miliony', 'milionů')),
        (1000, 'm', ('tisíc', 'tisíce', 'tisíc')),
    ]
    for value, g, forms in scales:
        if n >= value:
            count = n // value
            parts.append(_cs_below_1000(count, g))
            parts.append(cs_noun_form(count, *forms))
            n %= value
    if n:
        parts.append(_cs_below_1000(n, gender, compound=bool(parts)))
    return ' '.join(parts)


# ── Currency phrasing ────────────────────────────────────────────────────
CURRENCIES = {
    'EUR': {
        'en': (('euro', 'euros'), ('cent', 'cents')),
        'cs': ('n', ('euro', 'eura', 'eur'), ('cent', 'centy', 'centů')),
    },
    'USD': {
        'en': (('dollar', 'dollars'), ('cent', 'cents')),
        'cs': ('m', ('dolar', 'dolary', 'dolarů'), ('cent', 'centy', 'centů')),
    },
}


def _split(amount) -> tuple[int, int]:
    value = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if value < 0:
        raise ValueError('Negative amounts are not supported')
    whole = int(value)
    cents = int((value - whole) * 100)
    return whole, cents


def amount_in_words(amount, currency: str = 'EUR', lang: str = 'en') -> str:
    """
    >>> amount_in_words(Decimal('1234.50'), 'EUR', 'en')
    'One thousand two hundred thirty-four euros and 50 cents'
    >>> amount_in_words(Decimal('1234.50'), 'EUR', 'cs')
    'Jeden tisíc dvě stě třicet čtyři eura a 50 centů'
    """
    currency = (currency or 'EUR').upper()
    if currency not in CURRENCIES:
        raise ValueError(f'Unsupported currency: {currency}')
    whole, cents = _split(amount)
    if lang == 'cs':
        gender, major, minor = CURRENCIES[currency]['cs']
        words = int_to_words_cs(whole, gender)
        text = f'{words} {cs_noun_form(whole, *major)} a {cents:02d} {cs_noun_form(cents, *minor)}'
    else:
        major, minor = CURRENCIES[currency]['en']
        words = int_to_words_en(whole)
        major_word = major[0] if whole == 1 else major[1]
        minor_word = minor[0] if cents == 1 else minor[1]
        text = f'{words} {major_word} and {cents:02d} {minor_word}'
    return text[0].upper() + text[1:]


def format_money(amount, lang: str = 'cs') -> str:
    """cs → «1 234,50» (NBSP thousands), en → «1,234.50»."""
    value = Decimal(str(amount or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    sign = '-' if value < 0 else ''
    value = abs(value)
    whole = int(value)
    frac = int((value - whole) * 100)
    if lang == 'en':
        return f'{sign}{whole:,}.{frac:02d}'
    return f'{sign}' + f'{whole:,}'.replace(',', '\u00a0') + f',{frac:02d}'


def plain_amount(amount) -> str:
    """Machine-friendly amount for copying into banking apps: 1234.50"""
    value = Decimal(str(amount or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f'{value:.2f}'
