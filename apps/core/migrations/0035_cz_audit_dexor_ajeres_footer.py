"""Аудит prometeylabs.cz 19.10.2026 — правки після перевірки cz/release.

- №47: «TOV Dexor» → «Dexor» (title/title_cs/title_en + alt).
- №45: AJERES — чеський підзаголовок «Distributor potravin» (+ alt).
- №1: правовий рядок footer (SiteContactSettings legal_name_*/legal_address_* cs/en),
  тексти підтверджено Copy.

Оновлюється ЛИШЕ поле з точним старим значенням (адмін-правки не перетираються),
відкат симетричний. Нічого не видаляється. maison-polina не чіпається.
Ті самі значення — у seed (portfolio_* і SITE_CONTACT_DEFAULTS).
"""
from django.db import migrations

# (slug, field, old_value, new_value)
PORTFOLIO_CHANGES = [('ajeres', 'subtitle', 'Food distributor', 'Distributor potravin'),
 ('ajeres', 'subtitle_cs', 'Food distributor', 'Distributor potravin'),
 ('ajeres', 'card_image_alt', 'AJERES — food distributor', 'AJERES — distributor potravin'),
 ('ajeres', 'card_image_alt_cs', 'AJERES — food distributor', 'AJERES — distributor potravin'),
 ('deksor', 'title', 'TOV Dexor', 'Dexor'),
 ('deksor', 'title_cs', 'TOV Dexor', 'Dexor'),
 ('deksor', 'title_en', 'TOV Dexor', 'Dexor'),
 ('deksor', 'card_image_alt', 'TOV Dexor — digitální produkty', 'Dexor — digitální produkty'),
 ('deksor', 'card_image_alt_cs', 'TOV Dexor — digitální produkty', 'Dexor — digitální produkty'),
 ('deksor', 'card_image_alt_en', 'TOV Dexor — digital products', 'Dexor — digital products')]

# (field, old_value, new_value) для SiteContactSettings (singleton)
SITE_CONTACT_CHANGES = [('legal_name_cs',
  'Sofiia Dmytrenko, OSVČ',
  'Sofiia Dmytrenko, fyzická osoba podnikající podle ukrajinského práva (FOP)'),
 ('legal_name_en',
  'Sofiia Dmytrenko, Private Entrepreneur',
  'Sofiia Dmytrenko, sole trader (FOP, Ukraine)'),
 ('legal_address_cs', 'ul. Kvaši, d. 2, Myrhorod, Poltavská obl., Ukrajina', 'Myrhorod, Ukrajina'),
 ('legal_address_en', '2 Kvashi St, Myrhorod, Poltava Region, Ukraine', 'Myrhorod, Ukraine')]


def _apply(apps, portfolio, site):
    PortfolioProject = apps.get_model('core', 'PortfolioProject')
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    for slug, field, expected, value in portfolio:
        if slug == 'maison-polina':
            continue
        PortfolioProject.objects.filter(slug=slug, **{field: expected}).update(**{field: value})
    for field, expected, value in site:
        SiteContactSettings.objects.filter(**{field: expected}).update(**{field: value})


def forwards(apps, schema_editor):
    _apply(apps, PORTFOLIO_CHANGES, SITE_CONTACT_CHANGES)


def backwards(apps, schema_editor):
    _apply(
        apps,
        [(s, f, new, old) for s, f, old, new in PORTFOLIO_CHANGES],
        [(f, new, old) for f, old, new in SITE_CONTACT_CHANGES],
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_portfolioproject_is_ukraine_client_and_cz_audit'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
