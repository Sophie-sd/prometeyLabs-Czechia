"""Ідемпотентний seed demo-лендінгу PrometeyLabs (UA/EN/CS/RU).

Порядок: блоки → картки → галерея → до/після → відгуки → партнери.
Fallback-зображення — Pillow-плейсхолдер з `print(...)`-попередженням (ERR-74),
не мовчки.
"""
from __future__ import annotations

import hashlib
import io
import re
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw

from apps.demotenant.registry import ensure_registry_blocks

from .block_defaults import BLOCK_REGISTRY, IMAGE, TEXT
from .models import DEFAULT_THEME_COLORS
from .collection_models import (
    LandingBeforeAfter,
    LandingGalleryImage,
    LandingOffer,
    LandingPartner,
    LandingTestimonial,
)
from .content_models import LandingBlock
from .seed_data import BEFORE_AFTER, GALLERY, OFFERS, PARTNERS, TESTIMONIALS

SEED_ROOT = Path(settings.BASE_DIR) / 'static' / 'demolanding' / 'seed'


def seed_demo_landing(site) -> None:
    _seed_theme(site)
    _seed_hero(site)
    _seed_blocks(site)
    _seed_cta_image(site)
    _seed_offers(site)
    _seed_gallery(site)
    _seed_before_after(site)
    _seed_testimonials(site)
    _seed_partners(site)


def _seed_theme(site) -> None:
    changed = [
        field for field, value in DEFAULT_THEME_COLORS.items()
        if not getattr(site, field)
    ]
    if not changed:
        return
    for field in changed:
        setattr(site, field, DEFAULT_THEME_COLORS[field])
    site.save(update_fields=changed)


_GRAPHITE_NAME = re.compile(r'^(?:[0-9a-f]{12}-k|hero-kontur)(?:_[A-Za-z0-9]+)?\.webp$')
_LOUD_HASH = re.compile(r'^[0-9a-f]{12}(?:_[A-Za-z0-9]+)?\.webp$')


def _field_basename(name: str) -> str:
    return name.rsplit('/', 1)[-1] if name else ''


def _same_seed_name(stored_name: str, disk_name: str) -> bool:
    """Django FileField додає суфікс (`hero_ODxc683.webp`) — це той самий seed-файл."""
    stored = _field_basename(stored_name)
    if stored == disk_name:
        return True
    stem, _, ext = disk_name.rpartition('.')
    if not stem or not ext:
        return False
    stored_stem, _, stored_ext = stored.rpartition('.')
    if stored_ext != ext:
        return False
    if stored_stem == stem:
        return True
    prefix = f'{stem}_'
    if stored_stem.startswith(prefix):
        return bool(re.fullmatch(r'[A-Za-z0-9]+', stored_stem[len(prefix):]))
    return False


def _is_loud_placeholder(name: str) -> bool:
    if not name:
        return True
    base = _field_basename(name)
    if _GRAPHITE_NAME.match(base):
        return False
    return bool(_LOUD_HASH.match(base))


def _is_graphite_placeholder(name: str) -> bool:
    return bool(_GRAPHITE_NAME.match(_field_basename(name)))


def _graphite_photo(size: tuple[int, int], seed: str) -> ContentFile:
    width, height = size
    digest = hashlib.sha1(seed.encode('utf-8')).hexdigest()
    image = Image.new('RGB', (width, height), color='#1c1f1a')
    draw = ImageDraw.Draw(image)
    ox = int(digest[:2], 16) * width // 255 - width // 4
    oy = int(digest[2:4], 16) * height // 255 - height // 4
    draw.ellipse((ox, oy - height // 3, ox + int(width * 1.1), oy + int(height * 0.7)), fill='#2f341c')
    draw.ellipse((ox + width // 2, -height // 5, ox + int(width * 1.4), height // 2), fill='#3d4418')
    draw.ellipse((-width // 5, height // 2, width // 2, int(height * 1.2)), fill='#16181a')
    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=84)
    return ContentFile(buffer.getvalue(), name=f'{digest[:12]}-k.webp')


def _seed_file(relative: str, size: tuple[int, int]) -> ContentFile:
    disk = SEED_ROOT / relative
    if disk.is_file():
        return ContentFile(disk.read_bytes(), name=disk.name)
    print(f'[demolanding seed] missing {relative}, using graphite fallback')
    return _graphite_photo(size, relative)


def _assign_image(instance, field: str, relative: str, size: tuple[int, int]) -> bool:
    current = getattr(instance, field)
    name = current.name if current else ''
    disk = SEED_ROOT / relative
    if disk.is_file():
        replaceable = (
            not current
            or _is_loud_placeholder(name)
            or _is_graphite_placeholder(name)
            or _same_seed_name(name, disk.name)
        )
        if not replaceable:
            return False
        setattr(instance, field, ContentFile(disk.read_bytes(), name=disk.name))
        return True
    if current and not _is_loud_placeholder(name):
        return False
    setattr(instance, field, _seed_file(relative, size))
    return True


def _seed_hero(site) -> None:
    changed = []
    if _assign_image(site, 'hero_image', 'hero/hero.webp', (1920, 1080)):
        changed.append('hero_image')
    if _assign_image(site, 'hero_image_narrow', 'hero/hero-narrow.webp', (768, 1024)):
        changed.append('hero_image_narrow')
    if changed:
        site.save(update_fields=changed)


def _seed_blocks(site) -> None:
    ensure_registry_blocks(LandingBlock, site, BLOCK_REGISTRY)
    _apply_registry_copy(site)
    _seed_visible_flags(site)


def _apply_registry_copy(site) -> None:
    """Reseed перезаписує тексти й лейбли з реєстру — інакше лишається старий демо-контент."""
    for entry in BLOCK_REGISTRY:
        if entry['type'] == IMAGE:
            continue
        block, _created = LandingBlock.objects.get_or_create(
            tenant=site, page=entry['page'], key=entry['key'],
            defaults={
                'block_type': entry['type'],
                'label': str(entry['label']),
                'value_text': entry.get('default', '') if entry['type'] != IMAGE else '',
            },
        )
        block.block_type = entry['type']
        block.label = str(entry['label'])
        block.value_text = entry.get('default', '')
        if entry['type'] == TEXT:
            block.value_text_ru = entry.get('default_ru', '')
            block.value_text_en = entry.get('default_en', '')
            block.value_text_cs = entry.get('default_cs', '')
            block.save(update_fields=[
                'block_type', 'label', 'value_text', 'value_text_ru', 'value_text_en', 'value_text_cs',
            ])
        else:
            block.save(update_fields=['block_type', 'label', 'value_text'])


def _seed_visible_flags(site) -> None:
    keys = (
        ('stats', 'stats_visible'), ('offers', 'offers_visible'),
        ('process', 'process_visible'), ('gallery', 'gallery_visible'),
        ('before_after', 'before_after_visible'), ('reviews', 'reviews_visible'),
        ('faq', 'faq_visible'), ('footer', 'partners_visible'),
    )
    for page, key in keys:
        block = LandingBlock.objects.filter(tenant=site, page=page, key=key).first()
        if block and not block.value_text:
            block.value_text = '1'
            block.save(update_fields=['value_text'])


def _seed_cta_image(site) -> None:
    block = LandingBlock.objects.filter(tenant=site, page='cta', key='image').first()
    if not block:
        return
    if _assign_image(block, 'value_image', 'cta/cta.webp', (900, 1125)):
        block.save(update_fields=['value_image'])


def _seed_offers(site) -> None:
    keep_ids = []
    for order, data in enumerate(OFFERS):
        offer = LandingOffer.objects.filter(tenant=site, order=order).first()
        if offer is None:
            offer = LandingOffer(tenant=site, order=order)
        offer.title = data['title']
        offer.title_en = data['title_en']
        offer.title_cs = data['title_cs']
        offer.title_ru = data.get('title_ru', '')
        offer.description = data['description']
        offer.description_en = data['description_en']
        offer.description_cs = data['description_cs']
        offer.description_ru = data.get('description_ru', '')
        offer.price_from = data['price_from']
        offer.is_active = True
        offer.order = order
        offer.save()
        if _assign_image(offer, 'image', data['image'], (1200, 900)):
            offer.save(update_fields=['image'])
        keep_ids.append(offer.pk)
    LandingOffer.objects.filter(tenant=site).exclude(pk__in=keep_ids).delete()


def _seed_gallery(site) -> None:
    keep_ids = []
    for order, data in enumerate(GALLERY):
        item = LandingGalleryImage.objects.filter(tenant=site, order=order).first()
        if item is None:
            item = LandingGalleryImage(tenant=site, order=order)
        item.caption = data['caption']
        item.caption_en = data['caption_en']
        item.caption_cs = data['caption_cs']
        item.caption_ru = data.get('caption_ru', '')
        item.span = data['span']
        item.order = order
        _assign_image(item, 'image', data['image'], (1200, 900))
        item.save()
        keep_ids.append(item.pk)
    LandingGalleryImage.objects.filter(tenant=site).exclude(pk__in=keep_ids).delete()


def _seed_before_after(site) -> None:
    keep_ids = []
    for order, data in enumerate(BEFORE_AFTER):
        pair = LandingBeforeAfter.objects.filter(tenant=site, order=order).first()
        if pair is None:
            pair = LandingBeforeAfter(tenant=site, order=order)
        pair.title = data['title']
        pair.order = order
        changed = []
        if _assign_image(pair, 'image_before', data['before'], (1600, 900)):
            changed.append('image_before')
        if _assign_image(pair, 'image_after', data['after'], (1600, 900)):
            changed.append('image_after')
        pair.save()
        keep_ids.append(pair.pk)
    LandingBeforeAfter.objects.filter(tenant=site).exclude(pk__in=keep_ids).delete()


def _seed_testimonials(site) -> None:
    keep_ids = []
    for order, data in enumerate(TESTIMONIALS):
        review, _created = LandingTestimonial.objects.update_or_create(
            tenant=site, order=order,
            defaults={
                'author_name': data['author_name'], 'role': data['role'],
                'text': data['text'], 'text_en': data['text_en'],
                'text_cs': data['text_cs'], 'text_ru': data.get('text_ru', ''),
                'rating': data['rating'],
            },
        )
        keep_ids.append(review.pk)
    LandingTestimonial.objects.filter(tenant=site).exclude(pk__in=keep_ids).delete()


def _seed_partners(site) -> None:
    keep_ids = []
    for order, name in enumerate(PARTNERS):
        partner = LandingPartner.objects.filter(tenant=site, order=order).first()
        if partner is None:
            partner = LandingPartner(tenant=site, order=order)
        partner.name = name
        partner.order = order
        _assign_image(partner, 'logo', f'partners/{name.lower()}.webp', (240, 120))
        partner.save()
        keep_ids.append(partner.pk)
    LandingPartner.objects.filter(tenant=site).exclude(pk__in=keep_ids).delete()
