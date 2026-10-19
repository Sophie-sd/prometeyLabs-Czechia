"""Початкові дані портфоліо для seed_portfolio_projects.

Кожен проєкт — реальний сайт клієнта PrometeyLabs (`site_url`). Знімки головної
сторінки (`static_card` / `static_card_mobile`) генеруються локально командою
`capture_portfolio_screens` (Playwright) і кладуться у
`static/images/portfolio/screens/<slug>-desktop.webp` / `-mobile.webp`.
"""
from apps.core.portfolio_seed_projects_1 import PORTFOLIO_PROJECTS_1
from apps.core.portfolio_seed_projects_2 import PORTFOLIO_PROJECTS_2
from apps.core.portfolio_seed_projects_3 import PORTFOLIO_PROJECTS_3

PORTFOLIO_PROJECTS = PORTFOLIO_PROJECTS_1 + PORTFOLIO_PROJECTS_2 + PORTFOLIO_PROJECTS_3

IMAGE_FIELD_MAP = (
    ('static_card', 'card_image'),
    ('static_card_mobile', 'card_image_mobile'),
)

# Лого клієнтів на головній («Наші клієнти») — незалежно від PORTFOLIO_PROJECTS,
# щоб заміна портфоліо не ламала секцію. Ключ — Client.name.
HOME_LOGO_STATIC = {
    'SpeakUp': 'images/portfolio/speakup.png',
    'Coresync': 'images/portfolio/coresync.png',
    'Play Vision': 'images/portfolio/playvision.png',
    'BeautyShop': 'images/portfolio/beautyshop.png',
    'RedRabbit': 'images/portfolio/redrabbit.png',
    'Adiabatic': 'images/portfolio/adiabatic.png',
    'Polygraph': 'images/portfolio/polygraph.png',
    'Pulvas Store': 'images/portfolio/pulvas_store.png',
    'Airinua': 'images/portfolio/airinua.png',
}

# Клієнти для секції «Наші клієнти» на головній (seed_clients) — той самий
# набір лого, що й раніше на /portfolio/, до заміни на живі знімки.
HOME_CLIENTS = [
    {'name': 'Coresync', 'order': 0, 'static_home': HOME_LOGO_STATIC['Coresync']},
    {'name': 'SpeakUp', 'order': 1, 'static_home': HOME_LOGO_STATIC['SpeakUp']},
    {'name': 'Play Vision', 'order': 2, 'static_home': HOME_LOGO_STATIC['Play Vision']},
    {'name': 'BeautyShop', 'order': 3, 'static_home': HOME_LOGO_STATIC['BeautyShop']},
    {'name': 'Adiabatic', 'order': 4, 'static_home': HOME_LOGO_STATIC['Adiabatic']},
    {'name': 'RedRabbit', 'order': 5, 'static_home': HOME_LOGO_STATIC['RedRabbit']},
    {'name': 'Polygraph', 'order': 6, 'static_home': HOME_LOGO_STATIC['Polygraph']},
    {'name': 'Pulvas Store', 'order': 7, 'static_home': HOME_LOGO_STATIC['Pulvas Store']},
    {'name': 'Airinua', 'order': 8, 'static_home': HOME_LOGO_STATIC['Airinua']},
]

# №45 (аудит 19.10.2026): проєкти для клієнтів в Україні — під карткою підпис
# «Projekt pro klienta na Ukrajině» / «Project for a client in Ukraine».
# Seed виставляє прапорець лише при створенні рядка (fill-only), існуючі рядки
# оновлює міграція core.0034 тільки якщо там ще значення за замовчуванням.
# Не входять: ajeres (Узбекистан, EN-знімок), zatyshnyi-dvir (доставка
# Zásilkovna — уточнити країну), maison-polina (№46 — знято з портфоліо, core.0037).
UKRAINE_CLIENT_SLUGS = frozenset({
    'aniloks', 'auction-center', 'auto-lot', 'beauty-opt', 'beautycake', 'benzovoz',
    'boltiko', 'carpet-haus', 'caryvibe', 'choboty', 'deksor', 'diodi', 'distageavto',
    'domoteh', 'droproom', 'elit-fasad', 'evropobuts', 'fanera', 'favorit-metal',
    'fortprint', 'fpsu', 'geer', 'gordimarket', 'grand-oblik', 'kanalizacia',
    'krashiyvubir', 'krylova', 'kvest-marafon', 'magnum', 'metrium', 'molodii',
    'notenhaus', 'ofion', 'ogemed', 'oyra', 'phoenixvet', 'playvision', 'pokrivlya',
    'polygraph', 'queendrive', 'recharge', 'ruh-leo', 'school147', 'soliron',
    'speak-up', 'svitpc', 'tenclinic', 'ucvn', 'vezhi-rozhnovskogo', 'zelin',
    'znomax', 'zubroom',
})
