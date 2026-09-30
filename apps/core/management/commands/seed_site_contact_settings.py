"""
Ідемпотентне наповнення SiteContactSettings (контакти / адреса / карта).

Після деплою: python manage.py migrate && python manage.py seed_site_contact_settings
"""
from django.core.management.base import BaseCommand

from apps.core.models import SiteContactSettings
from apps.core.utils import SITE_CONTACT_DEFAULTS

# Fields owned by this CMS seed (P1). Social URLs left alone on update
# so prod customizations are not overwritten every deploy.
SEED_UPDATE_FIELDS = (
    'phone_display',
    'phone_e164',
    'address',
    'address_ru',
    'address_en',
    'address_cs',
    'czechia_address',
    'czechia_address_en',
    'czechia_address_cs',
    'legal_name',
    'legal_name_ru',
    'legal_name_en',
    'legal_name_cs',
    'registration_number',
    'legal_address',
    'legal_address_ru',
    'legal_address_en',
    'legal_address_cs',
    'data_protection_email',
    'maps_latitude',
    'maps_longitude',
    'maps_zoom',
    'google_maps_embed_url',
)


class Command(BaseCommand):
    help = (
        'Створює або оновлює singleton контактів сайту: CS+EN адреси з Україною, '
        'без телефону, з geo для карти'
    )

    def handle(self, *args, **options):
        obj, created = SiteContactSettings.objects.get_or_create(
            pk=1,
            defaults=SITE_CONTACT_DEFAULTS,
        )
        changed = []
        for key in SEED_UPDATE_FIELDS:
            value = SITE_CONTACT_DEFAULTS[key]
            current = getattr(obj, key)
            if current != value:
                setattr(obj, key, value)
                changed.append(key)

        if created or changed:
            obj.save()
            action = 'створено' if created else f'оновлено ({", ".join(changed)})'
        else:
            action = 'без змін (вже актуально)'

        self.stdout.write(
            self.style.SUCCESS(
                f'SiteContactSettings pk={obj.pk}: {action}. '
                f'phone_display={obj.phone_display!r}, '
                f'address_cs={obj.address_cs!r}, '
                f'address_en={obj.address_en!r}, '
                f'maps=({obj.maps_latitude}, {obj.maps_longitude}) z={obj.maps_zoom}'
            )
        )
