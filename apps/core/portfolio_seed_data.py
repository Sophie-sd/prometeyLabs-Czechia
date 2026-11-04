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

# `site_url` points at the client's English version wherever one exists (hreflang en,
# a language switch, or /en/ answering 200 with genuinely English content). The same
# address is used on the Czech and the English page. Two sites were checked and
# deliberately left on their original URL: carpet-haus.com.ua/en/ serves the Ukrainian
# page with only `lang="en"` swapped, and the four client logos in the home strip have
# no English version at all. See round2/link_mapping.md for the full audit.
IMAGE_FIELD_MAP = (
    ('static_card', 'card_image'),
    ('static_card_mobile', 'card_image_mobile'),
)

# Лого клієнтів на головній («Наші клієнти») — незалежно від PORTFOLIO_PROJECTS,
# щоб заміна портфоліо не ламала секцію. Ключ — Client.name.
HOME_LOGO_STATIC = {
    # Canon set (prometeylabs.com «Наші клієнти», 2026-11-03), same order and logos.
    'FPSU': 'images/clients/fpsu.webp',
    'Play Vision': 'images/clients/playvision.webp',
    'TEN clinic': 'images/clients/tenclinic.webp',
    'OFION': 'images/clients/ofion.webp',
    'Magnum': 'images/clients/magnum.webp',
    'ZNOMax': 'images/clients/znomax.webp',
    'UCVN': 'images/clients/ucvn.webp',
    'Svit PC': 'images/clients/svitpc.webp',
    'Boltiko': 'images/clients/boltiko.webp',
    'Domoteh': 'images/clients/domoteh.webp',
    'ZubRoom': 'images/clients/zubroom.webp',
    'Airinua': 'images/clients/airinua.webp',
    'GORDI market': 'images/clients/gordimarket.webp',
    'Kylymy': 'images/clients/kylymy.webp',
    'Oyra': 'images/clients/oyra.webp',
    'AJERES': 'images/clients/ajeres.webp',
    'Re-Charge': 'images/clients/recharge.webp',
    'Fortuna Print': 'images/clients/fortprint.webp',
    'Soliron': 'images/clients/soliron.webp',
    'Benzovoz': 'images/clients/benzovoz.webp',
    'Football Generation': 'images/clients/footballgeneration.webp',
    'Metrium': 'images/clients/metrium.webp',
    'Phoenix': 'images/clients/phoenixvet.webp',
    'Led Leader': 'images/clients/led-leader.webp',
    'Zelin': 'images/clients/zelin.webp',
    'Evropobut S': 'images/clients/evropobuts.webp',
    'Geer': 'images/clients/geer.webp',
    'DropRoom': 'images/clients/droproom.webp',
    'Beauty Cake': 'images/clients/beautycake.webp',
    'Queen Drive': 'images/clients/queendrive.webp',
    'DISTAGEavto': 'images/clients/distageavto.webp',
    'Pokrivlya': 'images/clients/pokrivlya.webp',
    'Umantransbud': 'images/clients/vezhi-rozhnovskogo.webp',
    # Kept from the earlier CZ set (not in canon) — listed for the owner, not deleted.
    'Coresync': 'images/portfolio/coresync.png',
    'Adiabatic': 'images/portfolio/adiabatic.png',
    'RedRabbit': 'images/portfolio/redrabbit.png',
    'Pulvas Store': 'images/portfolio/pulvas_store.png',
    # Retired from the strip (Ukrainian clients not in canon): row kept, is_active=False.
    'SpeakUp': 'images/portfolio/speakup.png',
    'BeautyShop': 'images/portfolio/beautyshop.png',
    'Polygraph': 'images/portfolio/polygraph.png',
}

# Клієнти для секції «Наші клієнти» на головній (seed_clients) — той самий
# набір лого, що й раніше на /portfolio/, до заміни на живі знімки.
# site_url: live address of the client's site, taken from PORTFOLIO_PROJECTS —
# the circle links there (dofollow, new tab) instead of /portfolio/.
# Coresync, Adiabatic, RedRabbit, Pulvas Store (no site) are hidden via RETIRED_HOME_CLIENTS.
HOME_CLIENTS = [
    {'name': 'FPSU', 'order': 0, 'static_home': HOME_LOGO_STATIC['FPSU'],
     'site_url': 'https://www.fpsu.org.ua/en/'},
    {'name': 'Play Vision', 'order': 1, 'static_home': HOME_LOGO_STATIC['Play Vision'],
     'site_url': 'https://playvision.com.ua/'},
    {'name': 'TEN clinic', 'order': 2, 'static_home': HOME_LOGO_STATIC['TEN clinic'],
     'site_url': 'https://tenclinic.com.ua/'},
    {'name': 'OFION', 'order': 3, 'static_home': HOME_LOGO_STATIC['OFION'],
     'site_url': 'https://ofion.com.ua/'},
    {'name': 'Magnum', 'order': 4, 'static_home': HOME_LOGO_STATIC['Magnum'],
     'site_url': 'https://magnum-tpc.com/en/'},
    {'name': 'ZNOMax', 'order': 5, 'static_home': HOME_LOGO_STATIC['ZNOMax'],
     'site_url': 'https://znomax.online/'},
    {'name': 'UCVN', 'order': 6, 'static_home': HOME_LOGO_STATIC['UCVN'],
     'site_url': 'https://ucvn.com.ua/en/'},
    {'name': 'Svit PC', 'order': 7, 'static_home': HOME_LOGO_STATIC['Svit PC'],
     'site_url': 'https://svitpc.com.ua/en/'},
    {'name': 'Boltiko', 'order': 8, 'static_home': HOME_LOGO_STATIC['Boltiko'],
     'site_url': 'https://boltiko.com.ua/'},
    {'name': 'Domoteh', 'order': 9, 'static_home': HOME_LOGO_STATIC['Domoteh'],
     'site_url': 'https://domoteh.shop/'},
    {'name': 'ZubRoom', 'order': 10, 'static_home': HOME_LOGO_STATIC['ZubRoom'],
     'site_url': 'https://zubroom.com.ua/'},
    {'name': 'Airinua', 'order': 11, 'static_home': HOME_LOGO_STATIC['Airinua'],
     'site_url': 'https://www.airinua.com/'},
    {'name': 'GORDI market', 'order': 12, 'static_home': HOME_LOGO_STATIC['GORDI market'],
     'site_url': 'https://gordimarket.com.ua/'},
    {'name': 'Kylymy', 'order': 13, 'static_home': HOME_LOGO_STATIC['Kylymy'],
     'site_url': 'https://carpet-haus.com.ua/'},
    {'name': 'Oyra', 'order': 14, 'static_home': HOME_LOGO_STATIC['Oyra'],
     'site_url': 'https://oyra.com.ua/'},
    {'name': 'AJERES', 'order': 15, 'static_home': HOME_LOGO_STATIC['AJERES'],
     'site_url': 'https://ajeres.uz/en/'},
    {'name': 'Re-Charge', 'order': 16, 'static_home': HOME_LOGO_STATIC['Re-Charge'],
     'site_url': 'https://recharge4gym.com.ua/en/'},
    {'name': 'Fortuna Print', 'order': 17, 'static_home': HOME_LOGO_STATIC['Fortuna Print'],
     'site_url': 'https://www.fortprint.com.ua/'},
    {'name': 'Soliron', 'order': 18, 'static_home': HOME_LOGO_STATIC['Soliron'],
     'site_url': 'https://soliron.com.ua/'},
    {'name': 'Benzovoz', 'order': 19, 'static_home': HOME_LOGO_STATIC['Benzovoz'],
     'site_url': 'https://www.benzovoz.com.ua/'},
    {'name': 'Football Generation', 'order': 20, 'static_home': HOME_LOGO_STATIC['Football Generation'],
     'site_url': 'https://footballgeneration.com.ua/'},
    {'name': 'Metrium', 'order': 21, 'static_home': HOME_LOGO_STATIC['Metrium'],
     'site_url': 'https://metrium.com.ua/'},
    {'name': 'Phoenix', 'order': 22, 'static_home': HOME_LOGO_STATIC['Phoenix'],
     'site_url': 'https://www.phoenixvet.com.ua/'},
    {'name': 'Led Leader', 'order': 23, 'static_home': HOME_LOGO_STATIC['Led Leader'],
     'site_url': 'https://led-leader.com.ua/en/'},
    {'name': 'Zelin', 'order': 24, 'static_home': HOME_LOGO_STATIC['Zelin'],
     'site_url': 'https://zelin.com.ua/'},
    {'name': 'Evropobut S', 'order': 25, 'static_home': HOME_LOGO_STATIC['Evropobut S'],
     'site_url': 'https://evropobuts.com.ua/'},
    {'name': 'Geer', 'order': 26, 'static_home': HOME_LOGO_STATIC['Geer'],
     'site_url': 'https://450geer.com.ua/'},
    {'name': 'DropRoom', 'order': 27, 'static_home': HOME_LOGO_STATIC['DropRoom'],
     'site_url': 'https://droproom.com.ua/'},
    {'name': 'Beauty Cake', 'order': 28, 'static_home': HOME_LOGO_STATIC['Beauty Cake'],
     'site_url': 'https://beautycake.com.ua/'},
    {'name': 'Queen Drive', 'order': 29, 'static_home': HOME_LOGO_STATIC['Queen Drive'],
     'site_url': 'https://queendrive.com.ua/'},
    {'name': 'DISTAGEavto', 'order': 30, 'static_home': HOME_LOGO_STATIC['DISTAGEavto'],
     'site_url': 'https://www.distageavto.com/uk/'},
    {'name': 'Pokrivlya', 'order': 31, 'static_home': HOME_LOGO_STATIC['Pokrivlya'],
     'site_url': 'https://pokrivlya.com.ua/'},
    {'name': 'Umantransbud', 'order': 32, 'static_home': HOME_LOGO_STATIC['Umantransbud'],
     'site_url': 'https://vezhi-rozhnovskogo.com.ua/'},
    # Not in canon, kept at the end until the owner decides (no English site known).
]

# Ukrainian clients that canon no longer shows: seed_clients hides them (is_active=False), never deletes.
# 04.11.2026 (Oleg): Coresync, Adiabatic, RedRabbit, Pulvas Store — no live site, hidden from the strip.
RETIRED_HOME_CLIENTS = (
    'SpeakUp', 'BeautyShop', 'Polygraph',
    'Coresync', 'Adiabatic', 'RedRabbit', 'Pulvas Store',
)

# Earlier seeded addresses that the seed may replace with the canon/English one
# (any other address typed in the admin is left alone).
LEGACY_CLIENT_SITE_URLS = frozenset({
    'https://www.playvision.com.ua/',
})

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
