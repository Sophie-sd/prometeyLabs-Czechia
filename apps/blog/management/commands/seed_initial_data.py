"""
Idempotent blog seed for PrometeyLabs Czechia (CS primary + EN).

After deploy (build.sh):
  python manage.py migrate && python manage.py seed_initial_data --prune

See docs/BLOG_TELEGRAM_SEED.md.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.blog.blog_seed_meta import BLOG_SEED_POSTS
from apps.blog.models import BlogPost

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'


def _load_i18n(lang: str) -> dict:
    path = DATA_DIR / f'blog_i18n_{lang}.json'
    with path.open(encoding='utf-8') as fh:
        return json.load(fh)


class Command(BaseCommand):
    help = 'Create or update blog posts (CS+EN) from apps/blog/data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prune',
            action='store_true',
            help='Delete posts whose slug is not in BLOG_SEED_POSTS',
        )

    def handle(self, *args, **options):
        cs_map = _load_i18n('cs')
        en_map = _load_i18n('en')
        seed_slugs = {item['slug'] for item in BLOG_SEED_POSTS}

        created = updated = skipped = 0

        for item in BLOG_SEED_POSTS:
            slug = item['slug']
            cs = cs_map.get(slug) or {}
            en = en_map.get(slug) or {}

            title_cs = (cs.get('title') or '').strip()
            title_en = (en.get('title') or title_cs).strip()
            if not title_cs:
                self.stderr.write(self.style.WARNING(f'Skip {slug}: missing CS title'))
                skipped += 1
                continue

            excerpt_cs = (cs.get('excerpt') or '').strip()
            excerpt_en = (en.get('excerpt') or excerpt_cs).strip()
            content_cs = (cs.get('content') or '').strip()
            content_en = (en.get('content') or content_cs).strip()
            keywords_cs = (cs.get('keywords') or '').strip()
            keywords_en = (en.get('keywords') or keywords_cs).strip()
            seo_title = (cs.get('seo_title') or title_cs)[:70]
            seo_description = (cs.get('seo_description') or excerpt_cs)[:160]

            y, m, d, hh, mm, ss = item['created']
            created_at = timezone.make_aware(datetime(y, m, d, hh, mm, ss))

            # Primary public fields = Czech; EN in *_en; clear RU; no UK on public.
            defaults = {
                'title': title_cs,
                'title_ru': '',
                'title_en': title_en,
                'title_cs': title_cs,
                'excerpt': excerpt_cs,
                'excerpt_ru': '',
                'excerpt_en': excerpt_en,
                'excerpt_cs': excerpt_cs,
                'content': content_cs,
                'content_ru': '',
                'content_en': content_en,
                'content_cs': content_cs,
                'keywords': keywords_cs,
                'keywords_ru': '',
                'keywords_en': keywords_en,
                'keywords_cs': keywords_cs,
                'seo_title': seo_title,
                'seo_description': seo_description,
                'meta_title': title_cs[:60],
                'meta_description': excerpt_cs[:160],
                'og_title': title_cs[:60],
                'og_description': excerpt_cs[:160],
                'category': item['category'],
                'reading_time': item['reading_time'],
                'is_published': True,
                'created_at': created_at,
            }

            post, was_created = BlogPost.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            # update_or_create may not force created_at on existing rows depending on
            # auto_now_add — set explicitly when provided.
            if post.created_at != created_at:
                BlogPost.objects.filter(pk=post.pk).update(created_at=created_at)

            if was_created:
                created += 1
                self.stdout.write(f'  + {slug}')
            else:
                updated += 1
                self.stdout.write(f'  ~ {slug}')

        pruned = 0
        if options['prune']:
            stale = BlogPost.objects.exclude(slug__in=seed_slugs)
            pruned = stale.count()
            stale.delete()

        self.stdout.write(self.style.SUCCESS(
            f'Blog seed done: created={created} updated={updated} '
            f'skipped={skipped} pruned={pruned} total_seed={len(seed_slugs)}'
        ))
