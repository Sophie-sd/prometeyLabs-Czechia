"""№46 (19.10.2026): зняти Maison Polina («Společnice») з публікації на .cz.

Рядок не видаляється міграцією — лише is_published / show_on_portfolio /
show_on_homepage = False. Проєкт прибрано з seed (portfolio_seed_projects_3,
portfolio_i18n_cs/en, portfolio_categories), тож seed його більше не поверне
(з --prune у build.sh рядок буде прибрано і з БД).
"""
from django.db import migrations

SLUG = 'maison-polina'


def unpublish(apps, schema_editor):
    PortfolioProject = apps.get_model('core', 'PortfolioProject')
    PortfolioProject.objects.filter(slug=SLUG).update(
        is_published=False,
        show_on_portfolio=False,
        show_on_homepage=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_merge_20261019_1246'),
    ]

    operations = [
        migrations.RunPython(unpublish, migrations.RunPython.noop),
    ]
