"""Portfolio categories (filters on /portfolio/, Figma 8ujBKCbHGm159yeTf0aObm 0:29).

`PortfolioProject.category` is the real data field behind the filter pills.
Labels live here per language (uk/ru/en/cs) so the page does not depend on
new .po msgids; existing project texts stay in the model / seed.
"""
from django.utils import translation

CATEGORY_SHOP = 'shop'
CATEGORY_LANDING = 'landing'
CATEGORY_CORPORATE = 'corporate'
CATEGORY_PLATFORM = 'platform'

# Order = order of the filter pills in Figma.
CATEGORY_ORDER = (CATEGORY_SHOP, CATEGORY_LANDING, CATEGORY_CORPORATE, CATEGORY_PLATFORM)

# Admin choices (uk, the admin language).
CATEGORY_CHOICES = (
    (CATEGORY_SHOP, 'Інтернет-магазин'),
    (CATEGORY_LANDING, 'Лендінг'),
    (CATEGORY_CORPORATE, 'Корпоративний сайт'),
    (CATEGORY_PLATFORM, 'Веб-платформа'),
)

FILTER_ALL = 'all'

# Plural labels (filter pills).
_FILTER_LABELS = {
    'uk': {
        FILTER_ALL: 'Усі проєкти',
        CATEGORY_SHOP: 'Інтернет-магазини',
        CATEGORY_LANDING: 'Лендінги',
        CATEGORY_CORPORATE: 'Корпоративні сайти',
        CATEGORY_PLATFORM: 'Веб-платформи',
    },
    'ru': {
        FILTER_ALL: 'Все проекты',
        CATEGORY_SHOP: 'Интернет-магазины',
        CATEGORY_LANDING: 'Лендинги',
        CATEGORY_CORPORATE: 'Корпоративные сайты',
        CATEGORY_PLATFORM: 'Веб-платформы',
    },
    'en': {
        FILTER_ALL: 'All projects',
        CATEGORY_SHOP: 'Online stores',
        CATEGORY_LANDING: 'Landing pages',
        CATEGORY_CORPORATE: 'Corporate websites',
        CATEGORY_PLATFORM: 'Web platforms',
    },
    'cs': {
        FILTER_ALL: 'Všechny projekty',
        CATEGORY_SHOP: 'E-shopy',
        CATEGORY_LANDING: 'Landing pages',
        CATEGORY_CORPORATE: 'Firemní weby',
        CATEGORY_PLATFORM: 'Webové platformy',
    },
}

# Singular labels (category pill on each project card).
_CARD_LABELS = {
    'uk': {
        CATEGORY_SHOP: 'Інтернет-магазин',
        CATEGORY_LANDING: 'Лендінг',
        CATEGORY_CORPORATE: 'Корпоративний сайт',
        CATEGORY_PLATFORM: 'Веб-платформа',
    },
    'ru': {
        CATEGORY_SHOP: 'Интернет-магазин',
        CATEGORY_LANDING: 'Лендинг',
        CATEGORY_CORPORATE: 'Корпоративный сайт',
        CATEGORY_PLATFORM: 'Веб-платформа',
    },
    'en': {
        CATEGORY_SHOP: 'Online store',
        CATEGORY_LANDING: 'Landing page',
        CATEGORY_CORPORATE: 'Corporate website',
        CATEGORY_PLATFORM: 'Web platform',
    },
    'cs': {
        CATEGORY_SHOP: 'E-shop',
        CATEGORY_LANDING: 'Landing page',
        CATEGORY_CORPORATE: 'Firemní web',
        CATEGORY_PLATFORM: 'Webová platforma',
    },
}

_PAGE_COPY = {
    'uk': {
        'lead': 'Сайти, що допомагають бізнесу залучати клієнтів, підвищувати довіру та зростати.',
        'filters_title': 'Оберіть категорію та перегляньте реалізовані проєкти:',
        'filters_aria': 'Фільтр проєктів за категорією',
        'scroll_label': 'До проєктів',
        'empty': 'Поки що в цій категорії немає проєктів.',
        'reset': 'Показати всі проєкти',
        'card_filter_hint': 'Показати всі проєкти категорії',
    },
    'ru': {
        'lead': 'Сайты, которые помогают бизнесу привлекать клиентов, повышать доверие и расти.',
        'filters_title': 'Выберите категорию и посмотрите реализованные проекты:',
        'filters_aria': 'Фильтр проектов по категории',
        'scroll_label': 'К проектам',
        'empty': 'В этой категории пока нет проектов.',
        'reset': 'Показать все проекты',
        'card_filter_hint': 'Показать все проекты категории',
    },
    'en': {
        'lead': 'Websites that help businesses win clients, build trust and grow.',
        'filters_title': 'Choose a category and browse the projects we have delivered:',
        'filters_aria': 'Filter projects by category',
        'scroll_label': 'To the projects',
        'empty': 'There are no projects in this category yet.',
        'reset': 'Show all projects',
        'card_filter_hint': 'Show all projects in category',
    },
    'cs': {
        'lead': 'Weby, které firmám pomáhají získávat klienty, budovat důvěru a růst.',
        'filters_title': 'Vyberte kategorii a prohlédněte si realizované projekty:',
        'filters_aria': 'Filtr projektů podle kategorie',
        'scroll_label': 'K projektům',
        'empty': 'V této kategorii zatím nejsou žádné projekty.',
        'reset': 'Zobrazit všechny projekty',
        'card_filter_hint': 'Zobrazit všechny projekty kategorie',
    },
}

# Category by slug for seed + data migration (same catalogue in Renova / Czechia).
CATEGORY_BY_SLUG = {
    # Web platforms: accounts, subscriptions, CRM, PWA.
    'znomax': CATEGORY_PLATFORM,
    'ucvn': CATEGORY_PLATFORM,
    'playvision': CATEGORY_PLATFORM,
    'auto-lot': CATEGORY_PLATFORM,
    # Online stores: catalogue + cart + payment.
    'ofion': CATEGORY_SHOP,
    'zatyshnyi-dvir': CATEGORY_SHOP,
    'droproom': CATEGORY_SHOP,
    'beauty-opt': CATEGORY_SHOP,
    'gordimarket': CATEGORY_SHOP,
    'domoteh': CATEGORY_SHOP,
    'carpet-haus': CATEGORY_SHOP,
    'svitpc': CATEGORY_SHOP,
    'geer': CATEGORY_SHOP,
    'oyra': CATEGORY_SHOP,
    'boltiko': CATEGORY_SHOP,
    'beautycake': CATEGORY_SHOP,
    'soliron': CATEGORY_SHOP,
    'ogemed': CATEGORY_SHOP,
    # Landing pages.
    'auction-center': CATEGORY_LANDING,
    'elit-fasad': CATEGORY_LANDING,
    'distageavto': CATEGORY_LANDING,
    'grand-oblik': CATEGORY_LANDING,
    'evropobuts': CATEGORY_LANDING,
    'fanera': CATEGORY_LANDING,
    'molodii': CATEGORY_LANDING,
    'aniloks': CATEGORY_LANDING,
    'queendrive': CATEGORY_LANDING,
    'choboty': CATEGORY_LANDING,
    'maison-polina': CATEGORY_LANDING,
    'zelin': CATEGORY_LANDING,
    # Everything else (catalogue + request, clinics, organisations) = corporate.
}


def category_for_slug(slug):
    return CATEGORY_BY_SLUG.get(slug, CATEGORY_CORPORATE)


def _lang():
    lang = (translation.get_language() or 'uk').split('-')[0]
    return lang if lang in _PAGE_COPY else 'uk'


def card_label(category):
    labels = _CARD_LABELS[_lang()]
    return labels.get(category) or labels[CATEGORY_CORPORATE]


def portfolio_filter_context(projects):
    """Filter pills with counts from the real `category` field + page copy."""
    lang = _lang()
    labels = _FILTER_LABELS[lang]
    counts = {key: 0 for key in CATEGORY_ORDER}
    for project in projects:
        if project.category in counts:
            counts[project.category] += 1
    filters = [{'key': FILTER_ALL, 'label': labels[FILTER_ALL], 'count': len(projects)}]
    filters += [
        {'key': key, 'label': labels[key], 'count': counts[key]}
        for key in CATEGORY_ORDER
    ]
    return {
        'portfolio_filters': filters,
        'portfolio_copy': _PAGE_COPY[lang],
    }
