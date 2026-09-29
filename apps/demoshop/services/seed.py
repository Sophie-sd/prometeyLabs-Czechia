"""Ідемпотентний seed демо-магазину: контент, каталог, hero, відгуки, фото.

Контракт мінімуму — seed_demo_shop_skill (ERR-31): усі видимі фічі вітрини
мають хоч один рядок даних. Ідемпотентність: update_or_create по slug.
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from ..block_defaults import BLOCK_REGISTRY
from ..catalog_models import ShopCategory, ShopProduct, ShopProductImage, ShopReview
from ..content_models import ShopBlock, ShopHeroSlide
from .images import load_seed_image

CATEGORY_SEED = [
    # (name/default=CS, name_ru unused, name_en, name_cs, icon)
    ('Elektronika', '', 'Electronics', 'Elektronika', '📱'),
    ('Dům a domácnost', '', 'Home & Living', 'Dům a domácnost', '🏠'),
    ('Doplňky', '', 'Accessories', 'Doplňky', '🎒'),
    ('Novinky', '', 'New Arrivals', 'Novinky', '✨'),
]

# Іменовані SKU + slug ассета в static/demoshop/seed/products/<slug>.webp
PRODUCT_SEED = [
    {
        'name': 'Bezdrátová sluchátka Aura',
        'name_ru': '',
        'name_en': 'Aura Wireless Headphones',
        'name_cs': 'Bezdrátová sluchátka Aura',
        'slug': 'wireless-headphones', 'cat': 0, 'price': 2490, 'featured': True
    },
    {
        'name': 'Chytré hodinky Horizon',
        'name_ru': '',
        'name_en': 'Horizon Smart Watch',
        'name_cs': 'Chytré hodinky Horizon',
        'slug': 'smart-watch', 'cat': 0, 'price': 3990, 'featured': True
    },
    {
        'name': 'Přenosný reproduktor Echo',
        'name_ru': '',
        'name_en': 'Echo Portable Speaker',
        'name_cs': 'Přenosný reproduktor Echo',
        'slug': 'portable-speaker', 'cat': 0, 'price': 1890, 'featured': True
    },
    {
        'name': 'Stolní lampa Lumen',
        'name_ru': '',
        'name_en': 'Lumen Desk Lamp',
        'name_cs': 'Stolní lampa Lumen',
        'slug': 'desk-lamp', 'cat': 1, 'price': 1290, 'featured': True
    },
    {
        'name': 'Organizér na stůl Craft',
        'name_ru': '',
        'name_en': 'Craft Desk Organizer',
        'name_cs': 'Organizér na stůl Craft',
        'slug': 'desk-organizer', 'cat': 1, 'price': 790, 'featured': False
    },
    {
        'name': 'Termohrnek Ceramic Soft',
        'name_ru': '',
        'name_en': 'Ceramic Soft Thermo Mug',
        'name_cs': 'Termohrnek Ceramic Soft',
        'slug': 'thermo-mug', 'cat': 1, 'price': 590, 'featured': True
    },
    {
        'name': 'Městský batoh Trail',
        'name_ru': '',
        'name_en': 'Trail City Backpack',
        'name_cs': 'Městský batoh Trail',
        'slug': 'city-backpack', 'cat': 2, 'price': 2190, 'featured': True
    },
    {
        'name': 'Obal na telefon SoftCase',
        'name_ru': '',
        'name_en': 'SoftCase Phone Case',
        'name_cs': 'Obal na telefon SoftCase',
        'slug': 'phone-case', 'cat': 2, 'price': 390, 'featured': False
    },
    {
        'name': 'Powerbanka Charge 20K',
        'name_ru': '',
        'name_en': 'Charge 20K Power Bank',
        'name_cs': 'Powerbanka Charge 20K',
        'slug': 'power-bank', 'cat': 0, 'price': 1190, 'featured': False
    },
    {
        'name': 'Sada nádobí Stoneware',
        'name_ru': '',
        'name_en': 'Stoneware Dishware Set',
        'name_cs': 'Sada nádobí Stoneware',
        'slug': 'dishware-set', 'cat': 1, 'price': 1590, 'featured': False
    },
    {
        'name': 'Fleecová deka Cloud',
        'name_ru': '',
        'name_en': 'Cloud Fleece Blanket',
        'name_cs': 'Fleecová deka Cloud',
        'slug': 'fleece-blanket', 'cat': 1, 'price': 990, 'featured': False
    },
    {
        'name': 'Aromatická svíčka Amber',
        'name_ru': '',
        'name_en': 'Amber Scented Candle',
        'name_cs': 'Aromatická svíčka Amber',
        'slug': 'aroma-candle', 'cat': 1, 'price': 450, 'featured': False
    },
    {
        'name': 'Podložka na jógu Balance',
        'name_ru': '',
        'name_en': 'Balance Yoga Mat',
        'name_cs': 'Podložka na jógu Balance',
        'slug': 'yoga-mat', 'cat': 3, 'price': 890, 'featured': False
    },
    {
        'name': 'Herní sluchátka Pulse',
        'name_ru': '',
        'name_en': 'Pulse Gaming Headset',
        'name_cs': 'Herní sluchátka Pulse',
        'slug': 'gaming-headset', 'cat': 0, 'price': 2790, 'featured': False
    },
    {
        'name': 'Držák na telefon Stand',
        'name_ru': '',
        'name_en': 'Stand Phone Holder',
        'name_cs': 'Držák na telefon Stand',
        'slug': 'phone-holder', 'cat': 2, 'price': 349, 'featured': False
    },
    {
        'name': 'Kabel USB-C Braided',
        'name_ru': '',
        'name_en': 'Braided USB-C Cable',
        'name_cs': 'Kabel USB-C Braided',
        'slug': 'usb-c-cable', 'cat': 2, 'price': 299, 'featured': False
    },
]

REVIEW_SEED = [
    {
        'author': 'Elena',
        'rating': 5,
        'product_slug': 'wireless-headphones',
        'text': (
            'Aura drží nabití dva pracovní dny. '
            'V metru nic nesviští, ani na maximum.'
        ),
    },
    {
        'author': 'Igor',
        'rating': 5,
        'product_slug': 'city-backpack',
        'text': (
            'Trail beru každý den: 15" notebook sedí rovně, '
            'zip se nezasekává ani po měsíci.'
        ),
    },
    {
        'author': 'Marie',
        'rating': 5,
        'product_slug': 'desk-lamp',
        'text': (
            'Lumen stojí na stole u okna. '
            'Večer je světlo teplé, oči neřeže.'
        ),
    },
    {
        'author': 'Adam',
        'rating': 4,
        'product_slug': 'power-bank',
        'text': (
            'Charge 20K nabíjel telefon dvakrát na cestě. '
            'Trochu těžší, než jsem čekal, ale drží.'
        ),
    },
    {
        'author': 'Natálie',
        'rating': 5,
        'product_slug': 'thermo-mug',
        'text': (
            'Káva v Ceramic Soft je teplá ještě v poledne. '
            'Víčko neteče v tašce — ověřeno.'
        ),
    },
    {
        'author': 'David',
        'rating': 5,
        'product_slug': 'portable-speaker',
        'text': (
            'Echo jsem vozil na chatu. Bas je v pohodě na tu velikost, '
            'sousedé si nestěžovali.'
        ),
    },
]

HERO_SLIDES_SEED = [
    # (title, title_ru, title_en, title_cs, subtitle..., cta..., images)
    (
        'Nová kolekce je tady', '', 'New collection is here', 'Nová kolekce je tady',
        'Vyberte si nejlepší za akční ceny, než zmizí', '',
        'Choose the best at promotional prices', 'Vyberte si nejlepší za akční ceny, než zmizí',
        'Do katalogu', '', 'To Catalog', 'Do katalogu',
        'hero/slide-1-wide.webp', 'hero/slide-1-narrow.webp',
    ),
    (
        'Doprava zdarma', '', 'Free Shipping', 'Doprava zdarma',
        'Při objednávce nad 1 500 Kč po celé ČR', '',
        'For orders over 1 500 Kč across Czechia', 'Při objednávce nad 1 500 Kč po celé ČR',
        'Zjistit více', '', 'Learn More', 'Zjistit více',
        'hero/slide-2-wide.webp', 'hero/slide-2-narrow.webp',
    ),
    (
        'Záruka vrácení 14 dní', '', '14-Day Return Guarantee', 'Záruka vrácení 14 dní',
        'Nakupujte s jistotou — vrácení bez otázek', '',
        'Shop with confidence — no-questions-asked returns', 'Nakupujte s jistotou — vrácení bez otázek',
        'Vybrat produkt', '', 'Choose a Product', 'Vybrat produkt',
        'hero/slide-3-wide.webp', 'hero/slide-3-narrow.webp',
    ),
]

GIFT_PROMO_SLUGS = {'wireless-headphones', 'aroma-candle'}


def _seed_blocks(shop, force_images: bool = False) -> None:
    for entry in BLOCK_REGISTRY:
        block, created = ShopBlock.objects.get_or_create(
            shop=shop,
            page=entry['page'],
            key=entry['key'],
            defaults={
                'block_type': entry['type'],
                'label': str(entry['label']),
                'value_text': entry.get('default', ''),
                'value_text_ru': entry.get('default_ru', ''),
                'value_text_en': entry.get('default_en', ''),
                'value_text_cs': entry.get('default_cs', ''),
            },
        )
        # Backfill локалей для блоків, створених до додавання en/ru/cs.
        if not created and not block.value_text_ru and entry.get('default_ru'):
            block.value_text_ru = entry['default_ru']
            block.save(update_fields=['value_text_ru'])
        if not created and not block.value_text_en and entry.get('default_en'):
            block.value_text_en = entry['default_en']
            block.save(update_fields=['value_text_en'])
        if not created and not block.value_text_cs and entry.get('default_cs'):
            block.value_text_cs = entry['default_cs']
            block.save(update_fields=['value_text_cs'])
        if entry['type'] != 'image':
            continue
        need_image = created or force_images or not block.value_image
        if need_image and entry['key'] == 'about_image':
            block.value_image = load_seed_image(
                'about/about.webp', fallback_label=shop.name, size=(2560, 1440),
            )
            block.save(update_fields=['value_image'])
        elif need_image:
            block.value_image = load_seed_image(
                'about/about.webp', fallback_label=shop.name, size=(1200, 720),
            )
            block.save(update_fields=['value_image'])


def _seed_categories(shop) -> list:
    categories = []
    for order, (name, name_ru, name_en, name_cs, icon) in enumerate(CATEGORY_SEED):
        category, created = ShopCategory.objects.get_or_create(
            shop=shop,
            name=name,
            defaults={
                'name_ru': name_ru,
                'name_en': name_en,
                'name_cs': name_cs,
                'icon': icon,
                'order': order
            },
        )
        if not created:
            fields = []
            if not category.name_ru:
                category.name_ru = name_ru
                fields.append('name_ru')
            if not category.name_en:
                category.name_en = name_en
                fields.append('name_en')
            if not category.name_cs:
                category.name_cs = name_cs
                fields.append('name_cs')
            if fields:
                category.save(update_fields=fields)
        categories.append(category)
    return categories


def _attach_product_image(product: ShopProduct, asset_slug: str, force: bool = False) -> None:
    existing = product.images.filter(is_main=True).first() or product.images.first()
    if existing and not force:
        return
    image_file = load_seed_image(
        f'products/{asset_slug}.webp',
        fallback_label=product.name,
        size=(800, 800),
    )
    if existing and force:
        existing.image.save(f'{asset_slug}.webp', image_file, save=True)
        existing.alt = product.name
        existing.is_main = True
        existing.save(update_fields=['alt', 'is_main'])
        return
    ShopProductImage.objects.create(
        product=product, image=image_file, alt=product.name, is_main=True,
    )


SEED_SLUGS = [item['slug'] for item in PRODUCT_SEED]


def _attach_gallery_extras(product: ShopProduct, asset_slug: str, force: bool = False) -> None:
    extra_slugs = [slug for slug in SEED_SLUGS if slug != asset_slug][:3]
    extras = product.images.filter(is_main=False)
    if force:
        extras.delete()
    have = product.images.filter(is_main=False).count()
    if have >= 3:
        return
    for index, slug in enumerate(extra_slugs):
        if index < have:
            continue
        image_file = load_seed_image(
            f'products/{slug}.webp',
            fallback_label=product.name,
            size=(800, 800),
        )
        ShopProductImage.objects.create(
            product=product,
            image=image_file,
            alt=product.name,
            is_main=False,
            order=index + 1,
        )


def _seed_products(shop, categories, force_images: bool = False) -> list:
    products = []
    now = timezone.now()
    keep_slugs = {item['slug'] for item in PRODUCT_SEED}
    for index, item in enumerate(PRODUCT_SEED):
        price = Decimal(item['price'])
        has_sale = index % 4 == 0
        old_price = (price * Decimal('1.25')).quantize(Decimal('1')) if has_sale else None
        sale_end = (now + timedelta(days=5 + (index % 5))) if has_sale else None

        gift = 'Mini svíčka jako dárek k objednávce' if item['slug'] in GIFT_PROMO_SLUGS else ''
        gift_ru = ''
        gift_en = 'Mini-candle as a gift with your order' if item['slug'] in GIFT_PROMO_SLUGS else ''
        gift_cs = 'Mini svíčka jako dárek k objednávce' if item['slug'] in GIFT_PROMO_SLUGS else ''

        product, _created = ShopProduct.objects.update_or_create(
            shop=shop,
            slug=item['slug'],
            defaults={
                'category': categories[item['cat'] % len(categories)],
                'name': item['name'],
                'name_ru': item['name_ru'],
                'name_en': item['name_en'],
                'name_cs': item['name_cs'],
                'short_description': 'Demo produkt pro testování katalogu, košíku a CMS.',
                'short_description_ru': '',
                'short_description_en': 'Demo product for testing catalog, cart and CMS.',
                'short_description_cs': 'Demo produkt pro testování katalogu, košíku a CMS.',
                'description': (
                    'Toto je ukázkový produkt s prémiovou fotografií. '
                    'Název, popis a obrázky upravíte v administraci „Můj obchod“.'
                ),
                'description_ru': '',
                'description_en': (
                    'This is a demo product with a premium photo. '
                    'Replace the title, description and images in the "My Shop" admin.'
                ),
                'description_cs': (
                    'Toto je demo produkt s prémiovou fotkou. '
                    'Změňte název, popis a obrázky v administraci „Můj obchod“.'
                ),
                'price': price,
                'old_price': old_price,
                'sale_end_date': sale_end,
                'gift_promo_text': gift,
                'gift_promo_text_ru': gift_ru,
                'gift_promo_text_en': gift_en,
                'gift_promo_text_cs': gift_cs,
                'is_featured': item['featured'],
                'is_active': True,
                'order': index,
            },
        )
        _attach_product_image(product, item['slug'], force=force_images)
        _attach_gallery_extras(product, item['slug'], force=force_images)
        products.append(product)

    # Прибираємо legacy №N товари зі старого seed (залишаємо лише канонічний каталог)
    ShopProduct.objects.filter(shop=shop).exclude(slug__in=keep_slugs).update(is_active=False)
    return products


def _seed_reviews(shop, products, force: bool = False) -> None:
    if shop.reviews.exists() and not force:
        return
    if force:
        shop.reviews.all().delete()
    by_slug = {product.slug: product for product in products}
    for item in REVIEW_SEED:
        ShopReview.objects.create(
            shop=shop,
            product=by_slug.get(item['product_slug']),
            author_name=item['author'],
            rating=item['rating'],
            text=item['text'],
        )


def _seed_hero_slides(shop, force_images: bool = False) -> None:
    for order, (
        title, title_ru, title_en, title_cs, sub, sub_ru, sub_en, sub_cs, cta, cta_ru, cta_en, cta_cs,
        wide_path, narrow_path,
    ) in enumerate(HERO_SLIDES_SEED):
        slide, created = ShopHeroSlide.objects.get_or_create(
            shop=shop,
            order=order,
            defaults={
                'title': title,
                'title_ru': title_ru,
                'title_en': title_en,
                'title_cs': title_cs,
                'subtitle': sub,
                'subtitle_ru': sub_ru,
                'subtitle_en': sub_en,
                'subtitle_cs': sub_cs,
                'cta_label': cta,
                'cta_label_ru': cta_ru,
                'cta_label_en': cta_en,
                'cta_label_cs': cta_cs,
                'is_active': True,
            },
        )
        if not created:
            slide_fields = []
            if not slide.title_en:
                slide.title_en = title_en
                slide.subtitle_en = sub_en
                slide.cta_label_en = cta_en
                slide_fields.extend(['title_en', 'subtitle_en', 'cta_label_en'])
            if not slide.title_cs:
                slide.title_cs = title_cs
                slide.subtitle_cs = sub_cs
                slide.cta_label_cs = cta_cs
                slide_fields.extend(['title_cs', 'subtitle_cs', 'cta_label_cs'])
            if slide_fields:
                slide.save(update_fields=slide_fields)

        need_images = created or force_images or not slide.image or not slide.image_narrow
        if need_images:
            wide = load_seed_image(wide_path, fallback_label=title, size=(2560, 1440))
            narrow = load_seed_image(narrow_path, fallback_label=title, size=(1080, 1620))
            slide.image.save(f'hero-{order}-wide.webp', wide, save=False)
            slide.image_narrow.save(f'hero-{order}-narrow.webp', narrow, save=False)
            if not slide.title_en:
                slide.title = title
                slide.title_ru = title_ru
                slide.title_en = title_en
                slide.title_cs = title_cs
                slide.subtitle = sub
                slide.subtitle_ru = sub_ru
                slide.subtitle_en = sub_en
                slide.subtitle_cs = sub_cs
                slide.cta_label = cta
                slide.cta_label_ru = cta_ru
                slide.cta_label_en = cta_en
                slide.cta_label_cs = cta_cs
            slide.save()


def seed_demo_shop(shop, force_images: bool = False, force_reviews: bool = False) -> None:
    """Ідемпотентно наповнює магазин мінімальним контрактом вітрини (ERR-31)."""
    _seed_blocks(shop, force_images=force_images)
    categories = _seed_categories(shop)
    products = _seed_products(shop, categories, force_images=force_images)
    _seed_reviews(shop, products, force=force_reviews)
    _seed_hero_slides(shop, force_images=force_images)
