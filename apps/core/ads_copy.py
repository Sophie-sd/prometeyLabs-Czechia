"""Literal copy for ads landings (cs/en). Visible FAQ and JSON-LD share these lists."""
from django.conf import settings
from django.utils import translation

SITE = (getattr(settings, 'CANONICAL_BASE', '') or 'https://prometeylabs.cz').rstrip('/')

SHOP_SLUGS = (
    'droproom', 'gordimarket', 'svitpc', 'ofion', 'beauty-opt',
    'domoteh', 'carpet-haus', 'geer', 'oyra', 'boltiko', 'beautycake', 'soliron',
)

PROCESS_SITE = {
    'cs': {
        'title': 'Jak tvoříme web',
        'note': 'Přesný čas závisí na složitosti designu a integrací — upřesníme na konzultaci',
        'steps': [
            ('Sběr informací', 'brief, cíle, publikum'),
            ('Mapa webu', 'struktura a navigace'),
            ('Návrh designu', 'UI/UX makety'),
            ('Funkční model', 'prototyp a logika formulářů'),
            ('Dokončení', 'testování na zařízeních'),
            ('Nasazení a předání', 'doména, SSL, přístupy, návody'),
        ],
    },
    'en': {
        'title': 'How we build a website',
        'note': 'Exact timing depends on design and integrations — we confirm it on a call',
        'steps': [
            ('Brief', 'goals and audience'),
            ('Sitemap', 'structure and navigation'),
            ('Design sample', 'UI/UX mockups'),
            ('Functional model', 'prototype and form logic'),
            ('Polish', 'testing on devices'),
            ('Deploy and handoff', 'domain, SSL, access, guides'),
        ],
    },
}

CONTACTS = {
    'cs': {
        'h2': 'Kontakty PrometeyLabs',
        'phone': '',
        'email': 'info@prometeylabs.com',
        'telegram': 'Telegram @prometeylabs',
        'address': 'Praha, Česko',
        'hours': 'Pracovní doba: nonstop',
        'executor': 'Zhotovitel: Sofiia Dmytrenko, veřejná smlouva —',
        'offer_label': '/offer/',
    },
    'en': {
        'h2': 'PrometeyLabs contacts',
        'phone': '',
        'email': 'info@prometeylabs.com',
        'telegram': 'Telegram @prometeylabs',
        'address': 'Prague, Czechia',
        'hours': 'Hours: around the clock',
        'executor': 'Contractor: Sofiia Dmytrenko, public offer —',
        'offer_label': '/offer/',
    },
}

CRUMBS = {
    'cs': {'home': 'Domů', 'services': 'Služby'},
    'en': {'home': 'Home', 'services': 'Services'},
}

SHOP = {
    'cs': {
        'title': 'Tvorba e-shopu na klíč — cena od 34 500 Kč | PrometeyLabs',
        'description': (
            'E-shop na klíč od 34 500 Kč: design, kód, platby a doprava (Zásilkovna, PPL, Česká pošta). '
            'Spuštění do 3 týdnů, 1 rok podpory zdarma.'
        ),
        'h1': 'Tvorba e-shopu na klíč',
        'line': (
            'Vývoj e-shopu od 34 500 Kč: spuštění do 3 týdnů, 1 rok podpory zdarma '
            'a doživotní záruka na kód.'
        ),
        'lead': 'Design, kód a integrace. Bez pluginů a bez měsíčního předplatného. E-shop zůstává váš.',
        'form_note': (
            'Manažer zavolá do 15 minut, odpoví na otázky a vybere balíček pro váš e-shop. '
            'Vaše údaje neprodáváme a nepoužíváme je k spamu.'
        ),
        'privacy_before': 'Odesláním poptávky souhlasíte s',
        'privacy_link': 'zásadami ochrany osobních údajů',
        'trust': (
            '30+ spuštěných e-shopů · Cena a termín ve smlouvě · '
            'Odpovídáme do 15 minut'
        ),
        'crumb': 'E-shopy',
        'portfolio_h2': 'Portfolio: e-shopy, které jsme spustili',
        'shops_note': 'Spustili jsme 30+ e-shopů — tady je výběr',
        'all_works': 'Všechny práce',
        'prices_h2': 'Kolik stojí tvorba e-shopu',
        'include_h3': 'Co je v Base',
        'include': (
            'katalog do 100 produktů, design, mobilní verze, základní SEO, '
            'platby, doprava (Zásilkovna / PPL / Česká pošta), administrace, košík, správa objednávek'
        ),
        'exclude_h3': 'Co není v ceně',
        'exclude': 'naplnění produktů, marketing, vlastní integrace; reklamní rozpočet se hradí zvlášť',
        'process_h2': 'Jak tvoříme e-shop: od briefu po spuštění za 14–21 dní',
        'offer_line': 'Záruku uvádíme ve veřejné smlouvě (čl. 8 nabídky)',
        'faq_h2': 'Časté otázky k tvorbě e-shopu',
        'faq': [
            (
                'Kolik stojí e-shop?',
                'Základní e-shop (do 100 produktů, design, mobilní verze, platby, doprava, administrace) — od 34 500 Kč. '
                'E-shop s CRM, Telegram upozorněními a nastavením reklamního účtu — individuální kalkulace. '
                'Přesnou částku a termín zapisujeme do smlouvy.',
            ),
            (
                'Jak dlouho trvá vývoj e-shopu?',
                'Spuštění do 3 týdnů (14–21 dní) pro e-shop s katalogem, košíkem, platbou a dopravou.',
            ),
            (
                'Bude měsíční poplatek nebo provize?',
                'Ne. Bez pluginů, bez měsíčního předplatného, bez provizí platforem. E-shop zůstává váš.',
            ),
            (
                'Jaká je záruka a podpora?',
                'Doživotní záruka na kód: technické chyby z naší strany opravíme zdarma, bez limitu doby. '
                'Plus 1 rok podpory zdarma: technické otázky, drobné úpravy a konzultace.',
            ),
            (
                'Převedete produkty z Shoptet, WooCommerce nebo jiného e-shopu?',
                'Ano. Import z existujícího katalogu, velké objemy SKU, migrace podle dohodnutého plánu.',
            ),
            (
                'Lze platit po etapách?',
                'Ano, platbu rozložíme do etap podle smlouvy. Podmínky zapisujeme před startem.',
            ),
            (
                'Je správa e-shopu složitá?',
                'Administrace v češtině: nový manažer ji zvládne do 15 minut. Zásoby, ceny a objednávky — v 1–2 kliknutích.',
            ),
        ],
    },
    'en': {
        'title': 'Turnkey online store — from CZK 34,500 | PrometeyLabs',
        'description': (
            'Turnkey online store from CZK 34,500: design, code, payments and Czech shipping '
            '(Packeta, PPL, Česká pošta). Launch in 3 weeks, 1 year of support free.'
        ),
        'h1': 'Turnkey online store',
        'line': (
            'Online store from CZK 34,500: launch in 3 weeks, 1 year of support free '
            'and a lifetime warranty on the code.'
        ),
        'lead': 'Design, code and integrations. No plugins and no monthly fee. The store stays yours.',
        'form_note': (
            'A manager will call within 15 minutes, answer questions and pick a package for your store. '
            'We do not sell your data or use it for spam.'
        ),
        'privacy_before': 'By sending the form you agree to the',
        'privacy_link': 'privacy policy',
        'trust': (
            '30+ launched stores · Price and timeline in the contract · '
            'We reply within 15 minutes'
        ),
        'crumb': 'Online stores',
        'portfolio_h2': 'Portfolio: online stores we launched',
        'shops_note': 'We have launched 30+ stores — here is a selection',
        'all_works': 'All work',
        'prices_h2': 'What an online store costs',
        'include_h3': 'What is in Base',
        'include': (
            'catalogue up to 100 products, design, mobile version, basic SEO, '
            'payments, shipping (Packeta / PPL / Česká pošta), admin, cart, order management'
        ),
        'exclude_h3': 'What is not included',
        'exclude': 'product filling, marketing, custom integrations; ad budget is paid separately',
        'process_h2': 'How we build a store: from brief to launch in 14–21 days',
        'offer_line': 'The warranty is in the public contract (clause 8 of the offer)',
        'faq_h2': 'FAQ about building an online store',
        'faq': [
            (
                'How much does an online store cost?',
                'A basic store (up to 100 products, design, mobile, payments, shipping, admin) — from CZK 34,500. '
                'A store with CRM, Telegram alerts and ad-account setup is quoted after the brief. '
                'We put the exact amount and timeline in the contract.',
            ),
            (
                'How long does development take?',
                'Launch in 3 weeks (14–21 days) for a store with catalogue, cart, payment and shipping.',
            ),
            (
                'Is there a monthly fee or commission?',
                'No. No plugins, no monthly fee, no platform commissions. The store stays yours.',
            ),
            (
                'What about warranty and support?',
                'Lifetime warranty on the code: bugs on our side are fixed free, with no time limit. '
                'Plus 1 year of support free: technical questions, small edits and consultations.',
            ),
            (
                'Will you migrate products from Shoptet, WooCommerce or another store?',
                'Yes. Import from an existing catalogue, large SKU volumes, migration on an agreed plan.',
            ),
            (
                'Can I pay in stages?',
                'Yes, we split payment into stages under the contract. Terms are written down before start.',
            ),
            (
                'Is the store hard to manage?',
                'Czech admin: a new manager learns it in 15 minutes. Stock, prices and orders — in 1–2 clicks.',
            ),
        ],
    },
}

RS = {
    'cs': {
        'title': 'Tvorba webu na klíč — od 10 000 Kč | PrometeyLabs',
        'description': (
            'Tvorba webů na klíč: landing 10 000–17 000 Kč, firemní web 17 000–24 500 Kč, '
            'e-shop od 34 500 Kč. Cena a termín ve smlouvě, rok podpory zdarma.'
        ),
        'crumb': 'Tvorba webu',
        'types_h2': 'Jaký typ webu zvolit',
        'types': [
            (
                'Landing',
                'Jedna stránka pod reklamu: nabídka, formulář a rychlé spuštění. Cena 10 000–17 000 Kč, termín 3–7 dní.',
                'corporate',
            ),
            (
                'Firemní web',
                'Struktura firmy, služby a SEO základ. Cena 17 000–24 500 Kč, termín 7–14 dní.',
                'corporate',
            ),
            (
                'E-shop',
                'Katalog, platba, doprava a objednávky v administraci. Cena od 34 500 Kč, termín 14–21 dní.',
                'shop',
            ),
            (
                'Platforma',
                'Kabinety, role a integrace. Cena 68 500–196 000 Kč, termín 14–30 dní.',
                'corporate',
            ),
        ],
        'more': 'Více:',
        'offer_line': 'Záruku uvádíme ve veřejné smlouvě (čl. 8 nabídky)',
        'guarantee_h2': 'Záruka a podpora',
        'guarantee': (
            'Doživotní záruka na kód a rok podpory zdarma. Zahrnuje: opravu technických chyb, '
            'udržení chodu kódu, reakci na kritické výpadky, soulad funkcí se zadáním. '
            'Nezahrnuje: nové funkce, změnu designu, integrace s novými službami.'
        ),
        'faq_h2': 'Časté otázky k tvorbě webu',
        'faq': [
            (
                'Kolik stojí web?',
                'Landing 10 000–17 000 Kč, firemní web 17 000–24 500 Kč, e-shop od 34 500 Kč, '
                'platforma 68 500–196 000 Kč. Přesnou částku a termín zapisujeme do smlouvy.',
            ),
            (
                'Jak dlouho trvá vývoj webu?',
                'Landing 3–7 dní, firemní web 7–14 dní, e-shop 14–21 dní, platforma 14–30 dní.',
            ),
            (
                'Co je v ceně?',
                'V ceně: maketa, sazba, formulář, responziv (landing); struktura stránek, CMS základ, responziv, základní SEO (firemní); '
                'katalog, košík, platba/doprava, správa objednávek (e-shop); dohodnuté MVP podle briefu (platforma). '
                'Není v ceně: reklama, texty od nuly, cizí API, naplnění obsahu, naplnění produktů, marketing, vlastní integrace.',
            ),
            (
                'Lze platit po etapách?',
                'Ano, platbu rozložíme do etap — bez skrytých podmínek. Podmínky jsou ve smlouvě.',
            ),
            (
                'Zvládnu web měnit sám?',
                'Texty, ceny, poptávky a bannery upravujete sami.',
            ),
            (
                'Jaká je záruka?',
                'Doživotní záruka na kód a rok podpory zdarma. Zahrnuje opravu technických chyb. '
                'Nezahrnuje nové funkce, změnu designu ani integrace s novými službami.',
            ),
        ],
    },
    'en': {
        'title': 'Turnkey website development — from CZK 10,000 | PrometeyLabs',
        'description': (
            'Turnkey websites: landing CZK 10,000–17,000, corporate CZK 17,000–24,500, '
            'online store from CZK 34,500. Price and timeline in the contract, a year of support free.'
        ),
        'crumb': 'Website development',
        'types_h2': 'Which type of website to choose',
        'types': [
            (
                'Landing page',
                'One page for ads: offer, form and a fast launch. CZK 10,000–17,000, 3–7 days.',
                'corporate',
            ),
            (
                'Corporate site',
                'Company structure, services and SEO basics. CZK 17,000–24,500, 7–14 days.',
                'corporate',
            ),
            (
                'Online store',
                'Catalogue, payment, shipping and orders in admin. From CZK 34,500, 14–21 days.',
                'shop',
            ),
            (
                'Platform',
                'Accounts, roles and integrations. CZK 68,500–196,000, 14–30 days.',
                'corporate',
            ),
        ],
        'more': 'More:',
        'offer_line': 'The warranty is in the public contract (clause 8 of the offer)',
        'guarantee_h2': 'Warranty and support',
        'guarantee': (
            'Lifetime warranty on the code and a year of support free. Includes: fixing technical bugs, '
            'keeping the code running, reacting to critical outages, matching the agreed spec. '
            'Does not include: new features, a design refresh, integrations with new services.'
        ),
        'faq_h2': 'FAQ about website development',
        'faq': [
            (
                'How much does a website cost?',
                'Landing CZK 10,000–17,000, corporate CZK 17,000–24,500, store from CZK 34,500, '
                'platform CZK 68,500–196,000. We put the exact amount and timeline in the contract.',
            ),
            (
                'How long does development take?',
                'Landing 3–7 days, corporate site 7–14 days, online store 14–21 days, platform 14–30 days.',
            ),
            (
                'What is included?',
                'Included: mockup, layout, form, responsive (landing); page structure, CMS base, responsive, basic SEO (corporate); '
                'catalogue, cart, payment/shipping, order admin (store); agreed MVP from the brief (platform). '
                'Not included: ads, copy from scratch, third-party APIs, content filling, product filling, marketing, custom integrations.',
            ),
            (
                'Can I pay in stages?',
                'Yes, we split payment into stages — no hidden terms. Terms are in the contract.',
            ),
            (
                'Can I edit the site myself?',
                'You edit texts, prices, leads and banners yourself.',
            ),
            (
                'What is the warranty?',
                'Lifetime warranty on the code and a year of support free. Includes fixing technical bugs. '
                'Does not include new features, a design refresh or integrations with new services.',
            ),
        ],
    },
}

CORP = {
    'cs': {
        'faq_h2': 'Časté otázky k firemním webům a landingům',
        'faq': [
            (
                'Kolik stojí web?',
                'Landing 10 000–17 000 Kč, firemní web 17 000–24 500 Kč. Přesnou částku a termín zapisujeme do smlouvy po briefu.',
            ),
            (
                'Jak dlouho trvá vývoj?',
                'Landing 3–7 dní, firemní web 7–14 dní, e-shop 14–21 dní, webová aplikace 14–30 dní. Přesný termín je ve smlouvě.',
            ),
            ('Lze platit po etapách?', 'Ano, podle smlouvy.'),
            (
                'Zvládnu web měnit sám?',
                'Ano. Administrace v češtině, texty, obrázky, ceny a služby měníte bez programátora.',
            ),
            ('Jaká je záruka?', 'Doživotní záruka na kód a 1 rok podpory zdarma.'),
            ('Budou v průběhu doplatky?', 'Ne, cenu dohodneme před startem.'),
            (
                'Mohu nejdřív získat konzultaci?',
                'Ano, krátká analýza webu zdarma. Nechte číslo, manažer zavolá do 15 minut.',
            ),
        ],
    },
    'en': {
        'faq_h2': 'FAQ about corporate websites and landing pages',
        'faq': [
            (
                'How much does a website cost?',
                'Landing CZK 10,000–17,000, corporate site CZK 17,000–24,500. We put the exact amount and timeline in the contract after the brief.',
            ),
            (
                'How long does development take?',
                'Landing 3–7 days, corporate site 7–14 days, online store 14–21 days, web app 14–30 days. The exact timeline is in the contract.',
            ),
            ('Can I pay in stages?', 'Yes, under the contract.'),
            (
                'Can I edit the site myself?',
                'Yes. Czech admin: texts, images, prices and services without a developer.',
            ),
            ('What is the warranty?', 'Lifetime warranty on the code and 1 year of support free.'),
            ('Will there be extra fees later?', 'No, we agree the price before start.'),
            (
                'Can I get a consultation first?',
                'Yes, a short website review free. Leave a number, a manager will call within 15 minutes.',
            ),
        ],
    },
}


def lang():
    code = (translation.get_language() or 'cs').split('-')[0]
    return 'en' if code == 'en' else 'cs'


def faq_pairs(items):
    return [{'q': q, 'a': a} for q, a in items]


def shop_copy():
    return SHOP[lang()]


def rs_copy():
    return RS[lang()]


def contacts_copy():
    return CONTACTS[lang()]


def crumbs_copy():
    return CRUMBS[lang()]


def process_site_copy():
    return PROCESS_SITE[lang()]


def corp_copy():
    return CORP[lang()]
