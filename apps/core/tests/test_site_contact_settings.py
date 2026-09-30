from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.utils import translation

from apps.core.context_processors import global_settings
from apps.core.models import SiteContactSettings
from apps.core.utils import get_site_contact_settings


class SiteContactSettingsTests(TestCase):
    def setUp(self):
        self.settings_obj, _ = SiteContactSettings.objects.get_or_create(pk=1)

    def test_singleton_second_create_raises(self):
        duplicate = SiteContactSettings(phone_e164='380000000000')
        with self.assertRaises(ValidationError):
            duplicate.save()

    def test_whatsapp_href_default_from_phone(self):
        self.settings_obj.phone_e164 = '380639520565'
        self.settings_obj.whatsapp_url = ''
        self.settings_obj.save()
        self.assertEqual(self.settings_obj.get_whatsapp_href(), 'https://wa.me/380639520565')

    def test_viber_href_default_from_phone(self):
        self.settings_obj.phone_e164 = '380639520565'
        self.settings_obj.viber_url = ''
        self.settings_obj.save()
        self.assertEqual(self.settings_obj.get_viber_href(), 'viber://add?number=380639520565')

    def test_maps_embed_from_coordinates(self):
        self.settings_obj.google_maps_embed_url = ''
        self.settings_obj.maps_latitude = '50.450100'
        self.settings_obj.maps_longitude = '30.523400'
        self.settings_obj.maps_zoom = 14
        self.settings_obj.save()
        src = self.settings_obj.get_maps_embed_src()
        self.assertIn('50.450100', src)
        self.assertIn('30.523400', src)
        self.assertIn('output=embed', src)

    def test_maps_embed_url_priority(self):
        self.settings_obj.google_maps_embed_url = 'https://www.google.com/maps/embed?pb=example'
        self.settings_obj.maps_latitude = '50.450100'
        self.settings_obj.maps_longitude = '30.523400'
        self.settings_obj.save()
        self.assertEqual(
            self.settings_obj.get_maps_embed_src(),
            'https://www.google.com/maps/embed?pb=example',
        )

    def test_context_processor_includes_site_contact(self):
        request = RequestFactory().get('/')
        context = global_settings(request)
        self.assertIn('site_contact', context)
        self.assertIsInstance(context['site_contact'], SiteContactSettings)

    def test_get_site_contact_settings_returns_pk_one(self):
        first = get_site_contact_settings()
        second = get_site_contact_settings()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.pk, 1)

    def test_localized_address_english(self):
        self.settings_obj.address = 'Київ, бульвар Тараса Шевченка 46а, Україна'
        self.settings_obj.address_en = '46a Taras Shevchenko Blvd, Kyiv, Ukraine'
        self.settings_obj.address_cs = 'bulvár Tarase Ševčenka 46a, Kyjev, Ukrajina'
        self.settings_obj.save()
        with translation.override('en'):
            self.assertEqual(
                self.settings_obj.get_localized_address(),
                '46a Taras Shevchenko Blvd, Kyiv, Ukraine',
            )

    def test_localized_address_czech(self):
        self.settings_obj.address = 'Київ, бульвар Тараса Шевченка 46а, Україна'
        self.settings_obj.address_en = '46a Taras Shevchenko Blvd, Kyiv, Ukraine'
        self.settings_obj.address_cs = 'bulvár Tarase Ševčenka 46a, Kyjev, Ukrajina'
        self.settings_obj.save()
        with translation.override('cs'):
            self.assertEqual(
                self.settings_obj.get_localized_address(),
                'bulvár Tarase Ševčenka 46a, Kyjev, Ukrajina',
            )


class SiteContactSeedTests(TestCase):
    def test_seed_clears_phone_and_sets_ukraine_addresses(self):
        from django.core.management import call_command
        from apps.core.utils import SITE_CONTACT_DEFAULTS

        obj, _ = SiteContactSettings.objects.get_or_create(pk=1)
        obj.phone_display = '+38 (063) 952-05-65'
        obj.phone_e164 = '380639520565'
        obj.address_en = '46a Taras Shevchenko Blvd, Kyiv'
        obj.address_cs = 'bulvár Tarase Ševčenka 46a, Kyjev'
        obj.maps_latitude = None
        obj.maps_longitude = None
        obj.save()

        call_command('seed_site_contact_settings')
        obj.refresh_from_db()

        self.assertEqual(obj.phone_display, '')
        self.assertEqual(obj.phone_e164, '')
        self.assertEqual(obj.address_en, SITE_CONTACT_DEFAULTS['address_en'])
        self.assertEqual(obj.address_cs, SITE_CONTACT_DEFAULTS['address_cs'])
        self.assertIn('Ukraine', obj.address_en)
        self.assertIn('Ukrajina', obj.address_cs)
        self.assertEqual(str(obj.maps_latitude), '50.444600')
        self.assertEqual(str(obj.maps_longitude), '30.505800')
        self.assertTrue(obj.get_maps_embed_src())

    def test_seed_is_idempotent(self):
        from django.core.management import call_command

        call_command('seed_site_contact_settings')
        call_command('seed_site_contact_settings')
        self.assertEqual(SiteContactSettings.objects.count(), 1)

    def test_localized_address_cs_en_from_seed(self):
        from django.core.management import call_command

        call_command('seed_site_contact_settings')
        obj = SiteContactSettings.objects.get(pk=1)
        with translation.override('en'):
            self.assertEqual(obj.get_localized_address(), obj.address_en)
        with translation.override('cs'):
            self.assertEqual(obj.get_localized_address(), obj.address_cs)
