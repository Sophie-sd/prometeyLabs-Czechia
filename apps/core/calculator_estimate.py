"""Орієнтовна оцінка вартості з відповідей калькулятора (EUR-база)."""
from __future__ import annotations

from decimal import Decimal

from django.utils.translation import gettext as _
from django.utils.translation import get_language

# Базові «від» у EUR — узгоджено з пакетами e-shop (ринок CZ, 09.2026).
BASE_MIN_EUR = {
    'A': 400,   # лендінг
    'B': 700,   # розширений лендінг / промо
    'C': 1000,  # корпоративний
    'D': 1600,  # інтернет-магазин
    'E': 2800,  # веб-додаток / PWA
}

PROJECT_LABELS = {
    'A': 'Лендінг (одна сторінка)',
    'B': 'Розширений лендінг / промо-сайт (багатосторінковий)',
    'C': 'Корпоративний сайт або сайт послуг',
    'D': 'Інтернет-магазин',
    'E': 'Веб-додаток / PWA',
}

TIMELINE_BY_Q3 = {
    'A': '3–14 днів',
    'B': '7–21 день',
    'C': '14–28 днів',
    'D': 'за домовленістю',
}

# Орієнтовні курси для підпису (не комерційний FX).
EUR_UAH = 43
EUR_CZK = 24.5

# Орієнтовна ціна в Kč округлюється до 500 Kč, половина — вгору (не round(): банківське). #40
CZK_ROUND_STEP = 500


def eur_to_czk_rounded(eur) -> int:
    """EUR → Kč за EUR_CZK, до найближчих 500 Kč (x.5 кроку — вгору). Точно через Decimal."""
    czk = Decimal(str(eur)) * Decimal(str(EUR_CZK))
    half = Decimal(CZK_ROUND_STEP) / 2
    return int((czk + half) // CZK_ROUND_STEP * CZK_ROUND_STEP)

# Надбавки в EUR (фіксовані).
ADDONS_EUR = {
    'q2_crm': 250,       # існуюча CRM / кабінет
    'q4_pay_card': 150,  # онлайн-оплата
    'q4_pay_multi': 300, # кілька способів
    'q3_urgent': 150,    # терміново
}


def _min_eur(answers: dict) -> int:
    q1 = answers.get('question_1') or 'A'
    total = BASE_MIN_EUR.get(q1, 400)

    q2 = answers.get('question_2') or []
    if isinstance(q2, str):
        q2 = [q2]
    if 'C' in q2 or 'D' in q2:
        total += ADDONS_EUR['q2_crm']

    q3 = answers.get('question_3')
    if q3 == 'A':
        total += ADDONS_EUR['q3_urgent']

    q4 = answers.get('question_4')
    if q4 == 'B':
        total += ADDONS_EUR['q4_pay_card']
    elif q4 == 'D':
        total += ADDONS_EUR['q4_pay_multi']
    elif q4 == 'C':
        total += 80

    return int(total)


def _format_number(n: int) -> str:
    return f'{n:,}'.replace(',', '\u00a0')


def format_price_display(min_eur: int, lang: str | None = None) -> dict:
    """Повертає primary + optional secondary рядок ціни."""
    lang = (lang or get_language() or 'uk').split('-')[0].lower()
    uah = int(round(min_eur * EUR_UAH))
    czk = eur_to_czk_rounded(min_eur)

    if lang in ('cs', 'en'):
        if lang == 'cs':
            primary = f'od {_format_number(min_eur)} €'
            secondary = f'orientačně ~{_format_number(czk)} Kč'
        else:
            primary = f'from €{_format_number(min_eur)}'
            secondary = f'approx. ~{_format_number(czk)} Kč'
        return {'price': primary, 'price_secondary': secondary, 'min_eur': min_eur}

    # uk, ru та інші — UAH
    if lang == 'ru':
        primary = f'от {_format_number(uah)} грн'
    else:
        primary = f'від {_format_number(uah)} грн'
    return {'price': primary, 'price_secondary': '', 'min_eur': min_eur}


def estimate_from_answers(answers: dict, lang: str | None = None) -> dict:
    """Словник для AJAX result: project_type, price, price_secondary, timeline."""
    lang = (lang or get_language() or 'uk').split('-')[0].lower()
    q1 = answers.get('question_1') or 'A'
    label_uk = PROJECT_LABELS.get(q1, PROJECT_LABELS['A'])
    # gettext на UA-джерелі
    project_type = _(label_uk)

    q3 = answers.get('question_3') or 'B'
    timeline = _(TIMELINE_BY_Q3.get(q3, TIMELINE_BY_Q3['B']))

    min_eur = _min_eur(answers)
    priced = format_price_display(min_eur, lang)

    return {
        'project_type': project_type,
        'price': priced['price'],
        'price_secondary': priced['price_secondary'],
        'timeline': timeline,
        'min_eur': min_eur,
    }
