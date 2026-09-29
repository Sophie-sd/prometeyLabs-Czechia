"""Seed-колекції demo-лендінгу PrometeyLabs Czechia (CS/EN — PrometeyLabs Czechia)."""

OFFERS = [
    {
        'title': 'Všechny potřebné bloky a menu',
        'title_en': 'All the blocks and menu you need',
        'title_cs': 'Všechny potřebné bloky a menu',
        'description': 'Hlavní obrazovka, výhody, příklady, recenze, otázky a formulář. Člověk se neztratí.',
        'description_en': 'Main screen, benefits, examples, reviews, questions and a form. Nobody gets lost.',
        'description_cs': 'Hlavní obrazovka, výhody, příklady, recenze, otázky a formulář. Člověk se neztratí.',
        'price_from': None, 'image': 'offers/turnkey.webp',
    },
    {
        'title': 'Sítě a poptávky',
        'title_en': 'Socials and requests',
        'title_cs': 'Sítě a poptávky',
        'description': 'Tlačítka na Instagram, Facebook a Telegram. Poptávka ze webu přijde vám.',
        'description_en': 'Buttons to Instagram, Facebook and Telegram. A request from the site comes to you.',
        'description_cs': 'Tlačítka na Instagram, Facebook a Telegram. Poptávka ze webu přijde vám.',
        'price_from': None, 'image': 'offers/renovation.webp',
    },
    {
        'title': 'Web upravujete sami',
        'title_en': 'You edit the site yourself',
        'title_cs': 'Web upravujete sami',
        'description': 'Texty, fotky a barvy v jednoduchém adminu. Bez programátora na každé «změňte slovo».',
        'description_en': 'Texts, photos and colors in a simple admin. No developer for every “change this word”.',
        'description_cs': 'Texty, fotky a barvy v jednoduchém adminu. Bez programátora na každé «změňte slovo».',
        'price_from': None, 'image': 'offers/facade.webp',
    },
    {
        'title': 'Rychle a pohodlně v telefonu',
        'title_en': 'Fast and easy on the phone',
        'title_cs': 'Rychle a pohodlně v telefonu',
        'description': 'Otevře se hned. Reklama míň utíká, protože stránka lidi neodrazuje.',
        'description_en': 'It opens right away. Ads waste less money because the page does not scare people away.',
        'description_cs': 'Otevře se hned. Reklama míň utíká, protože stránka lidi neodrazuje.',
        'price_from': None, 'image': 'offers/roof.webp',
    },
]

TESTIMONIALS = [
    {
        'author_name': 'Олена К.', 'role': 'Салон краси, Praha', 'rating': 5,
        'text': 'Lidé píšou sami, už desetkrát nevysvětluju služby v Directu.',
        'text_en': 'People write themselves — I no longer explain services in Direct ten times.',
        'text_cs': 'Lidé píšou sami, už desetkrát nevysvětluju služby v Directu.',
    },
    {
        'author_name': 'Ігор М.', 'role': 'Кавʼярня, Brno', 'rating': 5,
        'text': 'V telefonu je vše hned jasné. Poptávky na kávu chodí i v noci.',
        'text_en': 'Everything is clear on the phone. Coffee orders come even at night.',
        'text_cs': 'V telefonu je vše hned jasné. Poptávky na kávu chodí i v noci.',
    },
    {
        'author_name': 'Петро С.', 'role': 'Репетитор', 'rating': 5,
        'text': 'Jedna stránka místo tří sešitů na Instagramu.',
        'text_en': 'One page instead of three notebooks in Instagram.',
        'text_cs': 'Jedna stránka místo tří sešitů na Instagramu.',
    },
    {
        'author_name': 'Марина Т.', 'role': 'Клініка', 'rating': 5,
        'text': 'Poptávky v jednom adminu, texty měním sama za minutu.',
        'text_en': 'Requests in one admin — I change the texts myself in a minute.',
        'text_cs': 'Poptávky v jednom adminu, texty měním sama za minutu.',
    },
    {
        'author_name': 'Дмитро В.', 'role': 'Магазин', 'rating': 5,
        'text': 'Reklama je levnější: míň lidí utíká ze stránky.',
        'text_en': 'Ads got cheaper: fewer people run away from the page.',
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
     'caption': 'Páska, která jede sama', 'caption_en': 'A strip that moves by itself',
     'caption_cs': 'Páska, která jede sama'},
    {'image': 'gallery/site-4.webp', 'span': '1x1',
     'caption': 'Menu pohodlné v telefonu', 'caption_en': 'A menu that works on the phone',
     'caption_cs': 'Menu pohodlné v telefonu'},
    {'image': 'gallery/site-5.webp', 'span': '1x1',
     'caption': 'Čísla, která se načítají', 'caption_en': 'Numbers that count up',
     'caption_cs': 'Čísla, která se načítají'},
    {'image': 'gallery/site-6.webp', 'span': '1x1',
     'caption': 'Formulář, po kterém vám napíšou', 'caption_en': 'A form after which people write to you',
     'caption_cs': 'Formulář, po kterém vám napíšou'},
]

BEFORE_AFTER = [
    {'title': 'Сторінка з конструктора → зібрана під вас',
     'before': 'before_after/facade-before.webp',
     'after': 'before_after/facade-after.webp'},
    {'title': 'З телефону незручно → зручно з першого дотику',
     'before': 'before_after/roof-before.webp',
     'after': 'before_after/roof-after.webp'},
]
