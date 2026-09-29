"""Ідемпотентний seed demo-корпоративного сайту PrometeyLabs (UA/EN/CS/RU).

Без `reset_defaults` існуючі CMS-блоки й колекції не перезаписуються.
`refresh_images` перекладає hero / gallery / partners / about.photo з seed-файлів
без скидання текстів. Fallback — Pillow-плейсхолдер з `print(...)` (ERR-74).
Знімки карток каталогу — desktop-скріни з `/portfolio/`
(`static/images/portfolio/screens/<slug>-desktop.webp`). Інші зображення —
`static/democorp/seed`, потім demolanding.
"""
from __future__ import annotations

import io
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from apps.demotenant.registry import backfill_empty_locales, ensure_registry_blocks

from .block_defaults import BLOCK_REGISTRY
from .catalog_models import CorpCategory, CorpProduct, CorpProductImage
from .collection_models import CorpGalleryImage, CorpPartner, CorpProductionStep, CorpTestimonial
from .content_models import CorpBlock
from .models import DEFAULT_THEME_COLORS, LEGACY_THEME_COLORS
from .seed_data import CATEGORIES, GALLERY, PARTNERS, PRODUCTION_STEPS, PRODUCTS, TESTIMONIALS

STATIC_DIR = Path(settings.BASE_DIR) / 'static'

SEED_ROOT = Path(settings.BASE_DIR) / 'static' / 'democorp' / 'seed'
LANDING_SEED = Path(settings.BASE_DIR) / 'static' / 'demolanding' / 'seed'


def _atelier_image(relative_path: str, label: str, size=(800, 1066)) -> ContentFile:
    for root in (SEED_ROOT, LANDING_SEED, STATIC_DIR):
        path = root / relative_path
        if path.is_file():
            return ContentFile(path.read_bytes(), name=path.name)
    print(f'[democorp seed] missing image {relative_path}, using bark placeholder')
    width, height = size
    image = Image.new('RGB', (width, height), color='#181412')
    draw = ImageDraw.Draw(image)
    filename = Path(relative_path).name
    text = (label or Path(relative_path).stem)[:24]
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', max(18, width // 16))
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - text_w) / 2, (height - text_h) / 2), text, font=font, fill='#c99a44')
    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=82)
    return ContentFile(buffer.getvalue(), name=filename)


def seed_demo_corp(site, *, reset_defaults: bool = False, refresh_images: bool = False) -> None:
    _seed_blocks(site, reset=reset_defaults)
    _seed_production_steps(site, reset=reset_defaults)
    _seed_gallery(site, reset=reset_defaults, refresh_images=refresh_images)
    _seed_testimonials(site, reset=reset_defaults)
    _seed_partners(site, reset=reset_defaults, refresh_images=refresh_images)
    _seed_hero(site, reset=reset_defaults, refresh_images=refresh_images)
    _seed_about_photo(site, reset=reset_defaults, refresh_images=refresh_images)
    if reset_defaults:
        _reset_legacy_theme(site)
    if site.has_catalog:
        _seed_catalog(site, reset=reset_defaults, refresh_images=refresh_images)


def _seed_blocks(site, *, reset: bool) -> None:
    ensure_registry_blocks(CorpBlock, site, BLOCK_REGISTRY)
    backfill_empty_locales(CorpBlock, site, BLOCK_REGISTRY)
    if not reset:
        return
    for entry in BLOCK_REGISTRY:
        if entry['type'] == 'image':
            continue
        CorpBlock.objects.filter(tenant=site, page=entry['page'], key=entry['key']).update(
            label=str(entry['label']),
            block_type=entry['type'],
            value_text=entry.get('default', '') if entry['type'] != 'bool' else entry.get('default', '1'),
            value_text_ru=entry.get('default_ru', ''),
            value_text_en=entry.get('default_en', ''),
            value_text_cs=entry.get('default_cs', ''),
        )


def _reset_legacy_theme(site) -> None:
    changed = False
    legacy = {item.upper() for item in LEGACY_THEME_COLORS}
    for field, value in DEFAULT_THEME_COLORS.items():
        current = getattr(site, field) or ''
        if not current or current.upper() in legacy:
            setattr(site, field, value)
            changed = True
    if changed:
        site.save(update_fields=list(DEFAULT_THEME_COLORS.keys()))


def _seed_hero(site, *, reset: bool, refresh_images: bool = False) -> None:
    if site.hero_image and not reset and not refresh_images:
        return
    image = _atelier_image('hero/hero.webp', 'PrometeyLabs', size=(1200, 1600))
    site.hero_image = image
    site.save(update_fields=['hero_image'])


def _seed_about_photo(site, *, reset: bool, refresh_images: bool = False) -> None:
    block = CorpBlock.objects.filter(tenant=site, page='about', key='photo').first()
    if block is None:
        return
    if block.value_image and not reset and not refresh_images:
        return
    block.block_type = CorpBlock.BlockType.IMAGE
    block.value_image = _atelier_image('about/photo.webp', 'About', size=(900, 1200))
    block.save(update_fields=['block_type', 'value_image'])


def _seed_production_steps(site, *, reset: bool) -> None:
    if site.production_steps.exists() and not reset:
        return
    kept = []
    for order, data in enumerate(PRODUCTION_STEPS):
        step, _created = CorpProductionStep.objects.update_or_create(
            tenant=site, order=order,
            defaults={
                'title': data['title'], 'title_en': data['title_en'],
                'title_cs': data['title_cs'], 'title_ru': data['title_ru'],
                'description': data['description'], 'description_en': data['description_en'],
                'description_cs': data['description_cs'], 'description_ru': data['description_ru'],
            },
        )
        kept.append(step.pk)
    if reset:
        site.production_steps.exclude(pk__in=kept).delete()


def _seed_gallery(site, *, reset: bool, refresh_images: bool = False) -> None:
    if site.gallery_images.exists() and not reset and not refresh_images:
        return
    kept = []
    for order, data in enumerate(GALLERY):
        item, created = CorpGalleryImage.objects.update_or_create(
            tenant=site, kind=data['kind'], order=order,
            defaults={
                'caption': data['caption'],
                'caption_en': data.get('caption_en', ''),
                'caption_cs': data.get('caption_cs', ''),
                'caption_ru': data.get('caption_ru', ''),
            },
        )
        if created or not item.image or reset or refresh_images:
            item.image = _atelier_image(data['image'], data['caption'], size=(900, 1200))
            item.save(update_fields=['image'])
        kept.append(item.pk)
    if reset:
        site.gallery_images.exclude(pk__in=kept).delete()


def _seed_testimonials(site, *, reset: bool) -> None:
    if reset:
        site.testimonials.all().delete()
    for order, data in enumerate(TESTIMONIALS):
        CorpTestimonial.objects.get_or_create(
            tenant=site, order=order,
            defaults={
                'author_name': data['author_name'], 'role': data['role'],
                'text': data['text'],
                'text_en': data.get('text_en', ''),
                'text_cs': data.get('text_cs', ''),
                'text_ru': data.get('text_ru', ''),
                'rating': data['rating'],
            },
        )


def _seed_partners(site, *, reset: bool, refresh_images: bool = False) -> None:
    if site.partners.exists() and not reset and not refresh_images:
        return
    kept = []
    for order, name in enumerate(PARTNERS):
        partner, created = CorpPartner.objects.update_or_create(
            tenant=site, order=order, defaults={'name': name},
        )
        if created or not partner.logo or reset or refresh_images:
            partner.logo = _atelier_image(f'partners/{name.lower()}.webp', name, size=(240, 120))
            partner.save(update_fields=['logo'])
        kept.append(partner.pk)
    if reset:
        site.partners.exclude(pk__in=kept).delete()


def _row_from_portfolio_project(project, order: int) -> dict:
    n = max(len(CATEGORIES), 1)
    return {
        'slug': project.slug[:220],
        'category': order % n,
        'name': project.title,
        'name_en': project.title_en or project.title,
        'name_cs': project.title_cs or project.title,
        'name_ru': project.title_ru or project.title,
        'excerpt': project.card_description,
        'excerpt_en': project.card_description_en or project.card_description,
        'excerpt_cs': project.card_description_cs or project.card_description,
        'excerpt_ru': project.card_description_ru or project.card_description,
        'specs': project.integrations,
        'specs_en': project.integrations_en or project.integrations,
        'specs_cs': project.integrations_cs or project.integrations,
        'specs_ru': project.integrations_ru or project.integrations,
        'price_from': None,
        'image': f'images/portfolio/screens/{project.slug}-desktop.webp',
    }


def _row_from_portfolio_dict(item: dict, order: int) -> dict:
    n = max(len(CATEGORIES), 1)
    title = item['title']
    return {
        'slug': item['slug'][:220],
        'category': order % n,
        'name': title,
        'name_en': item.get('title_en') or title,
        'name_cs': item.get('title_cs') or title,
        'name_ru': item.get('title_ru') or title,
        'excerpt': item.get('card_description', ''),
        'excerpt_en': item.get('card_description_en') or item.get('card_description', ''),
        'excerpt_cs': item.get('card_description_cs') or item.get('card_description', ''),
        'excerpt_ru': item.get('card_description_ru') or item.get('card_description', ''),
        'specs': item.get('integrations', ''),
        'specs_en': item.get('integrations_en') or item.get('integrations', ''),
        'specs_cs': item.get('integrations_cs') or item.get('integrations', ''),
        'specs_ru': item.get('integrations_ru') or item.get('integrations', ''),
        'price_from': None,
        'image': item.get('static_card') or f"images/portfolio/screens/{item['slug']}-desktop.webp",
    }


def _catalog_product_rows() -> list:
    from apps.core.models import PortfolioProject
    from apps.core.portfolio_seed_data import PORTFOLIO_PROJECTS

    live = list(
        PortfolioProject.objects.filter(is_published=True, show_on_portfolio=True)
        .order_by('order', 'title')[:8]
    )
    if live:
        return [_row_from_portfolio_project(project, index) for index, project in enumerate(live)]
    seeded = [item for item in PORTFOLIO_PROJECTS if item.get('show_on_portfolio')][:8]
    if seeded:
        return [_row_from_portfolio_dict(item, index) for index, item in enumerate(seeded)]
    return list(PRODUCTS)


def _seed_catalog(site, *, reset: bool, refresh_images: bool = False) -> None:
    if site.categories.exists() and not reset and not refresh_images:
        return
    if reset:
        site.products.all().delete()
        site.categories.all().delete()
    categories = []
    for order, data in enumerate(CATEGORIES):
        slug = slugify(data['name'], allow_unicode=True)[:160]
        category, _created = CorpCategory.objects.update_or_create(
            tenant=site, slug=slug,
            defaults={
                'name': data['name'], 'name_en': data['name_en'],
                'name_cs': data['name_cs'], 'name_ru': data['name_ru'],
                'order': order, 'is_active': True,
            },
        )
        categories.append(category)

    rows = _catalog_product_rows()
    kept_slugs = []
    for order, data in enumerate(rows):
        slug = (data.get('slug') or slugify(data['name'], allow_unicode=True))[:220]
        kept_slugs.append(slug)
        product, created = CorpProduct.objects.update_or_create(
            tenant=site, slug=slug,
            defaults={
                'category': categories[data['category']],
                'name': data['name'], 'name_en': data['name_en'],
                'name_cs': data['name_cs'], 'name_ru': data['name_ru'],
                'excerpt': data['excerpt'], 'excerpt_en': data['excerpt_en'],
                'excerpt_cs': data['excerpt_cs'], 'excerpt_ru': data['excerpt_ru'],
                'specs': data['specs'],
                'specs_en': data.get('specs_en', ''),
                'specs_cs': data.get('specs_cs', ''),
                'specs_ru': data.get('specs_ru', ''),
                'price_from': data['price_from'],
                'is_featured': True,
                'is_active': True,
                'order': order,
            },
        )
        if created or not product.images.exists() or reset or refresh_images:
            product.images.all().delete()
            image = _atelier_image(data['image'], data['name_en'] or data['name'], size=(1440, 900))
            CorpProductImage.objects.create(product=product, image=image, is_main=True, order=0)
    site.products.exclude(slug__in=kept_slugs).delete()
