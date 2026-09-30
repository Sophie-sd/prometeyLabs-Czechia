"""Утиліти для apps.core."""
from decimal import Decimal

from django.core.cache import cache

from .models import SiteContactSettings

SITE_CONTACT_CACHE_KEY = 'site_contact_settings'
SITE_CONTACT_CACHE_TTL = 300

# Kyiv, Taras Shevchenko Blvd 46a — same office used on live contacts copy.
SITE_CONTACT_MAP_LAT = Decimal('50.444600')
SITE_CONTACT_MAP_LNG = Decimal('30.505800')
SITE_CONTACT_MAP_ZOOM = 15

SITE_CONTACT_DEFAULTS = {
    # Phone intentionally empty for Czechia public contacts (messenger/email only).
    'phone_display': '',
    'phone_e164': '',
    'email': 'info@prometeylabs.com',
    'address': 'Київ, бульвар Тараса Шевченка 46а, Україна',
    'address_ru': 'Киев, бульвар Тараса Шевченко 46а, Украина',
    'address_en': '46a Taras Shevchenko Blvd, Kyiv, Ukraine',
    'address_cs': 'bulvár Tarase Ševčenka 46a, Kyjev, Ukrajina',
    'legal_name': 'ФОП Дмитренко Софія Дмитрівна',
    'legal_name_ru': 'ФЛП Дмитренко София Дмитриевна',
    'legal_name_en': 'Sofiia Dmytrenko, Private Entrepreneur',
    'legal_name_cs': 'Sofiia Dmytrenko, OSVČ',
    'registration_number': '3770706565',
    'legal_address': 'Полтавська обл., м. Миргород, вул. Кваші, буд 2, Україна',
    'legal_address_ru': 'Полтавская обл., г. Миргород, ул. Кваши, дом 2, Украина',
    'legal_address_en': '2 Kvashi St, Myrhorod, Poltava Region, Ukraine',
    'legal_address_cs': 'ul. Kvaši, d. 2, Myrhorod, Poltavská obl., Ukrajina',
    'data_protection_email': 'info@prometeylabs.com',
    'instagram_url': 'https://instagram.com/prometeylabs',
    'facebook_url': 'https://www.facebook.com/profile.php?id=61577585882254',
    'linkedin_url': 'https://www.linkedin.com/in/sofia-dmitrenko',
    'telegram_url': 'https://t.me/prometeylabs',
    'tiktok_url': 'https://tiktok.com/@prometeylabs',
    'whatsapp_url': '',
    'viber_url': '',
    'maps_latitude': SITE_CONTACT_MAP_LAT,
    'maps_longitude': SITE_CONTACT_MAP_LNG,
    'maps_zoom': SITE_CONTACT_MAP_ZOOM,
    'google_maps_embed_url': '',
}


def get_site_contact_settings():
    """Повертає singleton налаштувань контактів (кеш ~5 хв)."""
    cached = cache.get(SITE_CONTACT_CACHE_KEY)
    if cached is not None:
        return cached

    settings_obj, _created = SiteContactSettings.objects.get_or_create(
        pk=1,
        defaults=SITE_CONTACT_DEFAULTS,
    )
    cache.set(SITE_CONTACT_CACHE_KEY, settings_obj, SITE_CONTACT_CACHE_TTL)
    return settings_obj
