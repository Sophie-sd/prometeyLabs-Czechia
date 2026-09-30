"""Seed-колекції demo-лендінгу PrometeyLabs Czechia (CS/EN — PrometeyLabs Czechia)."""

OFFERS = [
    {
        'title': 'Všechny potřebné bloky a menu',
        'title_en': 'All the blocks and menu you need',
        'title_cs': 'Všechny potřebné bloky a menu',
        'description': 'Hlavní obrazovka, výhody, příklady, recenze, otázky a formulář. Člověk se neztratí.',
        'description_en': 'Hero, benefits, examples, reviews, FAQ and a form. Nobody gets lost.',
        'description_cs': 'Hlavní obrazovka, výhody, příklady, recenze, otázky a formulář. Člověk se neztratí.',
        'price_from': None, 'image': 'offers/turnkey.webp',
    },
    {
        'title': 'Sítě a poptávky',
        'title_en': 'Socials and enquiries',
        'title_cs': 'Sítě a poptávky',
        'description': 'Tlačítka na Instagram, Facebook a Telegram. Poptávka ze webu přijde vám.',
        'description_en': 'Buttons to Instagram, Facebook and Telegram. An enquiry from the site comes to you.',
        'description_cs': 'Tlačítka na Instagram, Facebook a Telegram. Poptávka ze webu přijde vám.',
        'price_from': None, 'image': 'offers/renovation.webp',
    },
    {
        'title': 'Web upravujete sami',
        'title_en': 'You edit the site yourself',
        'title_cs': 'Web upravujete sami',
        'description': 'Texty, fotky a barvy v jednoduchém adminu. Bez programátora na každé «změňte slovo».',
        'description_en': 'Texts, photos and colours in a simple admin. No developer for every “change this word”.',
        'description_cs': 'Texty, fotky a barvy v jednoduchém adminu. Bez programátora na každé «změňte slovo».',
        'price_from': None, 'image': 'offers/facade.webp',
    },
    {
        'title': 'Rychle a pohodlně v telefonu',
        'title_en': 'Fast and comfortable on mobile',
        'title_cs': 'Rychle a pohodlně v telefonu',
        'description': 'Otevře se hned. Reklama míň utíká, protože stránka lidi neodrazuje.',
        'description_en': 'It opens right away. Ads convert better because the page doesn’t push people away.',
        'description_cs': 'Otevře se hned. Reklama míň utíká, protože stránka lidi neodrazuje.',
        'price_from': None, 'image': 'offers/roof.webp',
    },
]

TESTIMONIALS = [
    {
        'author_name': 'Elena K.', 'role': 'Salón krásy, Praha', 'rating': 5,
        'text': 'Lidé píšou sami, už desetkrát nevysvětluju služby v Directu.',
        'text_en': 'People reach out on their own — I no longer explain services in DMs ten times over.',
        'text_cs': 'Lidé píšou sami, už desetkrát nevysvětluju služby v Directu.',
    },
    {
        'author_name': 'Igor M.', 'role': 'Kavárna, Brno', 'rating': 5,
        'text': 'V telefonu je vše hned jasné. Poptávky na kávu chodí i v noci.',
        'text_en': 'Everything is clear on mobile. Coffee orders come even at night.',
        'text_cs': 'V telefonu je vše hned jasné. Poptávky na kávu chodí i v noci.',
    },
    {
        'author_name': 'Petr S.', 'role': 'Lektor', 'rating': 5,
        'text': 'Jedna stránka místo tří sešitů na Instagramu.',
        'text_en': 'One page instead of three Instagram notebooks.',
        'text_cs': 'Jedna stránka místo tří sešitů na Instagramu.',
    },
    {
        'author_name': 'Marina T.', 'role': 'Klinika', 'rating': 5,
        'text': 'Poptávky v jednom adminu, texty měním sama za minutu.',
        'text_en': 'Enquiries in one admin — I change the texts myself in a minute.',
        'text_cs': 'Poptávky v jednom adminu, texty měním sama za minutu.',
    },
    {
        'author_name': 'David V.', 'role': 'Obchod', 'rating': 5,
        'text': 'Reklama je levnější: míň lidí utíká ze stránky.',
        'text_en': 'Ads got cheaper: fewer people bounce from the page.',
        'text_cs': 'Reklama je levnější: míň lidí utíká ze stránky.',
    },
]

PARTNERS = ['Google', 'TikTok', 'Viber', 'YouTube', 'WhatsApp', 'Maps']

GALLERY = [
    {'image': 'gallery/site-1.webp', 'span': '1x1',
     'caption': 'Karty, které se naklánějí', 'caption_en': 'Cards that tilt',
     'caption_cs': 'Karty, které se naklánějí'},
    {'image': 'gallery/site-2.webp', 'span': '1x1',
     'caption': 'Před a po jedním prstem', 'caption_en': 'Before and after with one finger',
     'caption_cs': 'Před a po jedním prstem'},
    {'image': 'gallery/site-3.webp', 'span': '1x1',
     'caption': 'Páska, která jede sama', 'caption_en': 'A strip that moves on its own',
     'caption_cs': 'Páska, která jede sama'},
    {'image': 'gallery/site-4.webp', 'span': '1x1',
     'caption': 'Menu pohodlné v telefonu', 'caption_en': 'A menu that works on mobile',
     'caption_cs': 'Menu pohodlné v telefonu'},
    {'image': 'gallery/site-5.webp', 'span': '1x1',
     'caption': 'Čísla, která se načítají', 'caption_en': 'Numbers that count up',
     'caption_cs': 'Čísla, která se načítají'},
    {'image': 'gallery/site-6.webp', 'span': '1x1',
     'caption': 'Formulář, po kterém vám napíšou', 'caption_en': 'A form that brings enquiries',
     'caption_cs': 'Formulář, po kterém vám napíšou'},
]

BEFORE_AFTER = [
    # Single title field on LandingBeforeAfter — CS primary (public cs|en; EN via gettext N/A).
    {'title': 'Stránka z konstruktoru → sestavená pro vás',
     'before': 'before_after/facade-before.webp',
     'after': 'before_after/facade-after.webp'},
    {'title': 'Nepohodlné v telefonu → pohodlné od prvního dotyku',
     'before': 'before_after/roof-before.webp',
     'after': 'before_after/roof-after.webp'},
]
