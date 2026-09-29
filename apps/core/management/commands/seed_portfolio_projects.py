"""
Ідемпотентне наповнення портфоліо з static-зображень (CS primary + EN).

Після деплою (build.sh / start.sh):
  python manage.py migrate && python manage.py seed_portfolio_projects --prune

Див. docs/PORTFOLIO_SEED.md.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.core.models import PortfolioProject
from apps.core.portfolio_i18n import PORTFOLIO_I18N_CS, PORTFOLIO_I18N_EN
from apps.core.portfolio_seed_data import IMAGE_FIELD_MAP, PORTFOLIO_PROJECTS


class Command(BaseCommand):
    help = 'Створює або оновлює проєкти портфоліо (CS+EN) з static-контенту'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Перезаписати зображення навіть якщо вже завантажені',
        )
        parser.add_argument(
            '--prune',
            action='store_true',
            help='Видалити проєкти, яких немає у поточному PORTFOLIO_PROJECTS',
        )

    def handle(self, *args, **options):
        force_images = options['force_images']
        static_root = Path(settings.BASE_DIR) / 'static'
        created = 0
        updated = 0

        seed_slugs = {item['slug'] for item in PORTFOLIO_PROJECTS}

        for item in PORTFOLIO_PROJECTS:
            slug = item['slug']
            en = PORTFOLIO_I18N_EN.get(slug) or {}
            cs = PORTFOLIO_I18N_CS.get(slug) or {}

            title_cs = (cs.get('title') or item.get('title') or '').strip()
            title_en = (en.get('title') or title_cs).strip()
            subtitle_cs = (cs.get('subtitle') or item.get('subtitle') or '').strip()
            subtitle_en = (en.get('subtitle') or subtitle_cs).strip()
            desc_cs = (
                cs.get('card_description') or item.get('card_description') or ''
            ).strip()
            desc_en = (en.get('card_description') or desc_cs).strip()
            tags_cs = (cs.get('integrations') or item.get('integrations') or '').strip()
            tags_en = (en.get('integrations') or tags_cs).strip()
            alt_cs = (cs.get('card_image_alt') or item.get('card_image_alt') or title_cs).strip()
            alt_en = (en.get('card_image_alt') or title_en).strip()

            # Primary public fields = Czech; EN in *_en; no UK/RU on public fields.
            defaults = {
                'title': title_cs,
                'title_ru': '',
                'title_en': title_en,
                'title_cs': title_cs,
                'subtitle': subtitle_cs,
                'subtitle_ru': '',
                'subtitle_en': subtitle_en,
                'subtitle_cs': subtitle_cs,
                'card_description': desc_cs,
                'card_description_ru': '',
                'card_description_en': desc_en,
                'card_description_cs': desc_cs,
                'integrations': tags_cs,
                'integrations_ru': '',
                'integrations_en': tags_en,
                'integrations_cs': tags_cs,
                'card_image_alt': alt_cs,
                'card_image_alt_ru': '',
                'card_image_alt_en': alt_en,
                'card_image_alt_cs': alt_cs,
                'site_url': item.get('site_url', ''),
                'home_story_label': '',
                'home_story_label_ru': '',
                'modal_content': '',
                'modal_content_ru': '',
                'order': item.get('order', 0),
                'home_order': item.get('home_order', 0),
                'show_on_portfolio': item.get('show_on_portfolio', False),
                'show_on_homepage': item.get('show_on_homepage', False),
                'is_published': True,
            }
            project, was_created = PortfolioProject.objects.get_or_create(
                slug=slug,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                for key, value in defaults.items():
                    setattr(project, key, value)
                updated += 1

            self._attach_images(project, item, static_root, force_images)
            project.save()

        pruned = 0
        if options['prune']:
            stale = PortfolioProject.objects.exclude(slug__in=seed_slugs)
            pruned = stale.count()
            stale.delete()

        hidden = (
            PortfolioProject.objects.exclude(slug__in=seed_slugs)
            .filter(show_on_portfolio=True)
            .count()
        )
        PortfolioProject.objects.exclude(slug__in=seed_slugs).update(
            show_on_portfolio=False,
            show_on_homepage=False,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Портфоліо: створено {created}, оновлено {updated}, видалено {pruned}, '
                f'сховано застарілих {hidden}, '
                f'всього {PortfolioProject.objects.count()} записів.'
            )
        )

    def _attach_images(self, project, item, static_root, force_images):
        for static_key, field_name in IMAGE_FIELD_MAP:
            rel_path = item.get(static_key) or ''
            if not rel_path:
                continue
            field = getattr(project, field_name)
            if field and not force_images:
                media_path = Path(settings.MEDIA_ROOT) / field.name
                if media_path.is_file():
                    continue
            full_path = static_root / rel_path
            if not full_path.is_file():
                self.stdout.write(
                    self.style.WARNING(f'Файл не знайдено: {full_path}')
                )
                continue
            with full_path.open('rb') as handle:
                field.save(full_path.name, File(handle), save=False)
