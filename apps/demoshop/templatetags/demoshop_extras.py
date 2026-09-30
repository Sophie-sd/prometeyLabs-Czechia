"""Template-теги вітрини демо-магазину: CMS-тексти/фото, ideal_cols, money."""
from django import template

from apps.demoshop.content import get_image_url, get_text

register = template.Library()


@register.simple_tag
def block_text(shop, page, key, default=''):
    return get_text(getattr(shop, 'blocks_map', {}), page, key, default)


@register.simple_tag
def block_image(shop, page, key):
    return get_image_url(getattr(shop, 'blocks_map', {}), page, key)


@register.filter
def ideal_cols(count, max_cols=4):
    """Найбільша кількість колонок ≤ max_cols без «сироти» в останньому ряді."""
    try:
        count = int(count)
        max_cols = int(max_cols)
    except (TypeError, ValueError):
        return max_cols
    if count <= 0:
        return max_cols
    if count <= max_cols:
        return count
    for cols in range(max_cols, 1, -1):
        if count % cols == 0:
            return cols
    return max_cols


@register.filter
def tel_href(value):
    """Нормалізує CMS-телефон у tel:+… для iOS Safari."""
    raw = str(value or '')
    kept = ''.join(ch for ch in raw if ch.isdigit() or ch == '+')
    if not kept:
        return ''
    if kept.startswith('+'):
        return f'tel:{kept}'
    return f'tel:+{kept}'


@register.filter
def money(value):
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return value
    return f'{amount:,}'.replace(',', '\xa0')


@register.simple_tag(takes_context=True)
def currency_symbol(context):
    """Kč for public cs|en (Czechia); ₴ only if a legacy uk/ru locale is active."""
    request = context.get('request')
    lang = ''
    if request is not None:
        lang = getattr(request, 'LANGUAGE_CODE', '') or ''
    if not lang:
        from django.utils.translation import get_language
        lang = get_language() or 'cs'
    lang = lang.split('-')[0].lower()
    if lang in ('uk', 'ru'):
        return '₴'
    return 'Kč'


# Тематичні фото для Color Wipe карток категорій (static/demoshop/seed/…)
_CATEGORY_IMAGES = {
    # CS primary slugs (slugify allow_unicode) + ASCII fallbacks + legacy UA keys
    'elektronika': 'demoshop/seed/products/wireless-headphones.webp',
    'electronics': 'demoshop/seed/products/wireless-headphones.webp',
    'електроніка': 'demoshop/seed/products/wireless-headphones.webp',
    'dům-a-domácnost': 'demoshop/seed/products/desk-lamp.webp',
    'dum-a-domacnost': 'demoshop/seed/products/desk-lamp.webp',
    'home-living': 'demoshop/seed/products/desk-lamp.webp',
    'дім-і-побут': 'demoshop/seed/products/desk-lamp.webp',
    'doplňky': 'demoshop/seed/products/city-backpack.webp',
    'doplnky': 'demoshop/seed/products/city-backpack.webp',
    'accessories': 'demoshop/seed/products/city-backpack.webp',
    'аксесуари': 'demoshop/seed/products/city-backpack.webp',
    'novinky': 'demoshop/seed/products/portable-speaker.webp',
    'new-arrivals': 'demoshop/seed/products/portable-speaker.webp',
    'новинки': 'demoshop/seed/products/portable-speaker.webp',
}


@register.filter
def category_image(category):
    """Шлях static для тематичного фото категорії."""
    slug = (getattr(category, 'slug', '') or '').strip().lower()
    if slug in _CATEGORY_IMAGES:
        return _CATEGORY_IMAGES[slug]
    name = (getattr(category, 'name', '') or '').strip().lower()
    for key, path in _CATEGORY_IMAGES.items():
        if key in name or name in key:
            return path
    return 'demoshop/seed/products/wireless-headphones.webp'
