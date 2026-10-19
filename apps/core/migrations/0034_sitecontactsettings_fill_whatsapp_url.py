"""
Заповнює SiteContactSettings.whatsapp_url (підтверджено Олегом, 2026-10-19).

- forward: лише якщо поле порожнє/NULL — існуюче значення не перезаписується;
- reverse: очищає поле лише якщо воно досі дорівнює саме цьому URL;
- телефон (phone_e164 / phone_display) не чіпається;
- якщо singleton-рядка pk=1 немає — нічого не створюємо: рядок створює 0010
  або get_site_contact_settings()/seed з SITE_CONTACT_DEFAULTS.
Номер має бути лише в href (wa.me), не у видимому тексті.
"""
from django.db import migrations
from django.db.models import Q

WHATSAPP_URL = 'https://wa.me/380995891477'
SITE_CONTACT_CACHE_KEY = 'site_contact_settings'


def _clear_cache():
    try:
        from django.core.cache import cache
        cache.delete(SITE_CONTACT_CACHE_KEY)
    except Exception:
        pass


def fill_whatsapp_url(apps, schema_editor):
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    updated = (
        SiteContactSettings.objects
        .filter(Q(whatsapp_url__isnull=True) | Q(whatsapp_url=''))
        .update(whatsapp_url=WHATSAPP_URL)
    )
    if updated:
        _clear_cache()


def clear_own_whatsapp_url(apps, schema_editor):
    SiteContactSettings = apps.get_model('core', 'SiteContactSettings')
    updated = SiteContactSettings.objects.filter(whatsapp_url=WHATSAPP_URL).update(whatsapp_url='')
    if updated:
        _clear_cache()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_portfolioproject_category'),
    ]

    operations = [
        migrations.RunPython(fill_whatsapp_url, clear_own_whatsapp_url),
    ]
