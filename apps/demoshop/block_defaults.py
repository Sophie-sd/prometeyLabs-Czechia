"""Дефолтні CMS-блоки демо-магазину (registry-driven, редагування у «Мій магазин»)."""
from django.utils.translation import gettext_lazy as _

TEXT = 'text'
IMAGE = 'image'

PAGE_LABELS = {
    'header': _('Хедер і стрічка'),
    'home': _('Головна сторінка'),
    'catalog': _('Каталог'),
    'pdp': _('Картка товару'),
    'footer': _('Футер'),
}

BLOCK_REGISTRY = [
    {'page': 'header', 'key': 'shop_name', 'type': TEXT, 'label': _('Назва магазину (лого)'),
     'default': 'Demo Shop', 'default_en': 'Demo Shop', 'default_cs': 'Demo Shop'},
    {'page': 'header', 'key': 'announcement_text', 'type': TEXT, 'label': _('Текст бігучої стрічки'),
     'default': 'Doprava zdarma od 1 500 Kč · Platba při doručení · Vrácení do 14 dnů',
     'default_en': 'Free shipping from 1 500 Kč · Cash on delivery · 14-day returns',
     'default_cs': 'Doprava zdarma od 1 500 Kč · Platba při doručení · Vrácení do 14 dnů'},

    {'page': 'home', 'key': 'hero_title', 'type': TEXT, 'label': _('Заголовок hero'),
     'default': 'Vše pro pohodlný domov', 'default_en': 'Everything for a comfortable home',
     'default_cs': 'Vše pro pohodlný domov'},
    {'page': 'home', 'key': 'hero_subtitle', 'type': TEXT, 'label': _('Підзаголовок hero'), 'multiline': True,
     'default': 'Katalog ověřených produktů s rychlým doručením po celé ČR',
     'default_en': 'A catalogue of verified products with fast delivery across Czechia',
     'default_cs': 'Katalog ověřených produktů s rychlým doručením po celé ČR'},
    {'page': 'home', 'key': 'hero_cta_label', 'type': TEXT, 'label': _('Текст кнопки hero'),
     'default': 'Přejít do katalogu', 'default_en': 'View catalogue', 'default_cs': 'Přejít do katalogu'},
    {'page': 'home', 'key': 'about_title', 'type': TEXT, 'label': _('Заголовок «Про нас»'),
     'default': 'Proč si vybrat nás', 'default_en': 'Why choose us', 'default_cs': 'Proč si vybrat nás'},
    {'page': 'home', 'key': 'about_text', 'type': TEXT, 'label': _('Текст «Про нас»'), 'multiline': True,
     'default': 'Působíme od roku 2019 a objednávky odesíláme po celé zemi do 24 hodin.',
     'default_en': 'We’ve been operating since 2019 and ship orders nationwide within 24 hours.',
     'default_cs': 'Působíme od roku 2019 a objednávky odesíláme po celé zemi do 24 hodin.'},
    {'page': 'home', 'key': 'about_image', 'type': IMAGE, 'label': _('Фото «Про нас»')},
    {'page': 'home', 'key': 'stat_orders', 'type': TEXT, 'label': _('Статистика: замовлень'),
     'default': '12 400+', 'default_en': '12,400+', 'default_cs': '12 400+'},
    {'page': 'home', 'key': 'stat_clients', 'type': TEXT, 'label': _('Статистика: клієнтів'),
     'default': '8 900+', 'default_en': '8,900+', 'default_cs': '8 900+'},
    {'page': 'home', 'key': 'stat_rating', 'type': TEXT, 'label': _('Статистика: рейтинг'),
     'default': '4.9 / 5', 'default_en': '4.9 / 5', 'default_cs': '4.9 / 5'},

    {'page': 'catalog', 'key': 'catalog_title', 'type': TEXT, 'label': _('Заголовок каталогу'),
     'default': 'Katalog produktů', 'default_en': 'Product catalogue', 'default_cs': 'Katalog produktů'},
    {'page': 'catalog', 'key': 'catalog_subtitle', 'type': TEXT, 'label': _('Підзаголовок каталогу'),
     'default': 'Vyberte kategorii nebo použijte vyhledávání', 'default_en': 'Choose a category or use search',
     'default_cs': 'Vyberte kategorii nebo použijte vyhledávání'},

    {'page': 'pdp', 'key': 'delivery_text', 'type': TEXT, 'label': _('Вкладка «Доставка»'), 'multiline': True,
     'default': 'Doručení po celé zemi. Platba při převzetí. Vrácení do 14 dnů.',
     'default_en': 'Delivery nationwide. Pay on delivery. Returns within 14 days.',
     'default_cs': 'Doručení po celé zemi. Platba při převzetí. Vrácení do 14 dnů.'},

    {'page': 'footer', 'key': 'footer_text', 'type': TEXT, 'label': _('Текст футера'), 'multiline': True,
     'default': 'Demo obchod vygenerován společností PrometeyLabs Czechia jako ukázka CMS funkcí.',
     'default_en': 'Demo store by PrometeyLabs Czechia — an example of our CMS in action.',
     'default_cs': 'Demo obchod vygenerován společností PrometeyLabs Czechia jako ukázka CMS funkcí.'},
    {'page': 'footer', 'key': 'footer_phone', 'type': TEXT, 'label': _('Телефон у футері'),
     'default': '+420 777 000 000', 'default_en': '+420 777 000 000', 'default_cs': '+420 777 000 000'},
    {'page': 'footer', 'key': 'footer_email', 'type': TEXT, 'label': _('Email у футері'),
     'default': 'shop@example.com', 'default_en': 'shop@example.com', 'default_cs': 'shop@example.com'},
]


def get_block_entry(page: str, key: str):
    for entry in BLOCK_REGISTRY:
        if entry['page'] == page and entry['key'] == key:
            return entry
    return None
