from django.db import migrations, models

from apps.core.portfolio_categories import CATEGORY_BY_SLUG, CATEGORY_CHOICES


def set_categories(apps, schema_editor):
    PortfolioProject = apps.get_model('core', 'PortfolioProject')
    for slug, category in CATEGORY_BY_SLUG.items():
        PortfolioProject.objects.filter(slug=slug).update(category=category)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_lead_optional_name_czechia_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioproject',
            name='category',
            field=models.CharField(
                choices=CATEGORY_CHOICES,
                db_index=True,
                default='corporate',
                max_length=20,
                verbose_name='Категорія (фільтр /portfolio/)',
            ),
        ),
        migrations.RunPython(set_categories, migrations.RunPython.noop),
    ]
